import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import asyncio
from google.cloud import speech, vision
from langgraph.graph import Graph
from typing import Dict, Any
from core.config import PINECONE_API_KEY, GOOGLE_CREDENTIALS_PATH
from pinecone import Pinecone, ServerlessSpec

class ChatAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        index_name = "troubleshooter-index"
        if index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=index_name,
                dimension=1536,
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-west-2')
            )
        self.index = self.pc.Index(index_name)

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CREDENTIALS_PATH
        self.speech_client = speech.SpeechClient()
        self.vision_client = vision.ImageAnnotatorClient()

        self.graph = Graph()
        self.graph.add_node("input", self.input_node)
        self.graph.add_node("text_processing", self.text_processing_node)
        self.graph.add_node("voice_processing", self.voice_processing_node)
        self.graph.add_node("video_processing", self.video_processing_node)
        self.graph.add_node("issue_identification", self.issue_identification_node)
        self.graph.add_node("solution_retrieval", self.solution_retrieval_node)
        self.graph.add_node("response_generation", self.response_generation_node)

        self.graph.add_conditional_edges(
            "input",
            lambda state: state["input_type"],
            {"text": "text_processing", "voice": "voice_processing", "video": "video_processing"}
        )
        self.graph.add_edge("text_processing", "issue_identification")
        self.graph.add_edge("voice_processing", "issue_identification")
        self.graph.add_edge("video_processing", "issue_identification")
        self.graph.add_edge("issue_identification", "solution_retrieval")
        self.graph.add_edge("solution_retrieval", "response_generation")
        self.graph.set_entry_point("input")
        self.graph.set_finish_point("response_generation")
        self.app = self.graph.compile()

    def input_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Received input: type={state.get('input_type')}, data=<data>")
        return state

    async def text_processing_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state["processed_input"] = state.get("input_data", "")
        self.logger.info(f"Processed text input: {state['processed_input']}")
        return state

    async def voice_processing_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        audio_data = state.get("input_data", b"")
        if audio_data:
            try:
                audio = speech.RecognitionAudio(content=audio_data)
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    language_code='en-US'
                )
                response = self.speech_client.recognize(config=config, audio=audio)
                for result in response.results:
                    state["processed_input"] = result.alternatives[0].transcript
                    self.logger.info(f"Processed voice input: {state['processed_input']}")
                    return state
                state["processed_input"] = "No speech detected"
            except Exception as e:
                self.logger.error(f"Error processing voice: {e}")
                state["processed_input"] = "Error processing voice"
        else:
            state["processed_input"] = "No audio data provided"
        return state

    async def video_processing_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        video_data = state.get("input_data", b"")
        if video_data:
            try:
                image = vision.Image(content=video_data)  # Note: Needs frame extraction for real video
                response = self.vision_client.label_detection(image=image)
                labels = response.label_annotations
                state["processed_input"] = ", ".join([label.description for label in labels])
                self.logger.info(f"Processed video input: {state['processed_input']}")
            except Exception as e:
                self.logger.error(f"Error processing video: {e}")
                state["processed_input"] = "Error processing video"
        else:
            state["processed_input"] = "No video data provided"
        return state

    async def issue_identification_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        processed_input = state.get("processed_input", "").lower()
        self.logger.info(f"Identifying issue from: {processed_input}")
        if any(phrase in processed_input for phrase in ["no sound", "sound not working", "surround sound", "audio issue"]):
            state["issue"] = "no_sound"
        elif "tv not turning on" in processed_input:
            state["issue"] = "tv_not_turning_on"
        elif "settings" in processed_input:
            state["issue"] = "settings_issue"
        elif any(phrase in processed_input for phrase in ["flashing light", "error code"]):
            state["issue"] = "error_code"
        else:
            state["issue"] = "unknown"
        self.logger.info(f"Identified issue: {state['issue']}")
        return state

    async def solution_retrieval_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            query_vector = [0.1] * 1536  # Placeholder
            results = self.index.query(vector=query_vector, top_k=1, include_metadata=True)
            if results['matches']:
                state["solution"] = results['matches'][0]['metadata'].get('solution', "No solution found")
                self.logger.info(f"Retrieved solution from Pinecone: {state['solution']}")
                return state
        except Exception as e:
            self.logger.error(f"Pinecone query failed: {e}")

        solutions = {
            "no_sound": "Please check if the sound system is turned on and cables are connected.",
            "tv_not_turning_on": "Please check the power cable and ensure the TV is plugged in.",
            "settings_issue": "Navigate to the settings menu and verify the correct input source is selected.",
            "error_code": "The flashing light indicates an error; please note the pattern and consult the device manual."
        }
        state["solution"] = solutions.get(state["issue"], "Issue not recognized. Please provide more details.")
        self.logger.info(f"Retrieved fallback solution: {state['solution']}")
        return state

    async def response_generation_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state["response"] = state.get("solution", "No solution found.")
        self.logger.info(f"Generated response: {state['response']}")
        return state

    async def process_input(self, input_type: str, input_data: Any) -> str:
        state = {"input_type": input_type, "input_data": input_data}
        result = await self.app.ainvoke(state)
        return result["response"]

if __name__ == "__main__":
    async def test():
        agent = ChatAgent()
        response = await agent.process_input("text", "My TV has no sound.")
        print(f"Text Response: {response}")
        # For testing voice/video, you'd need to load bytes from files
        with open("/home/vincent/ixome/notebooks/test_audio.wav", "rb") as f:
            response = await agent.process_input("voice", f.read())
        print(f"Voice Response: {response}")
    asyncio.run(test())