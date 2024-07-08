# """
# Install the Google AI Python SDK

# $ pip install google-generativeai

# See the getting started guide for more information:
# https://ai.google.dev/gemini-api/docs/get-started/python
# """
# import os
# import google.generativeai as genai

# class ModelAdvisor:
#   PATH = 'advisor_examples'

#   def __init__(self):
#     self.genai = genai.configure(api_key=os.environ["GEMINI_API_KEY"])
#     # Create the model
#     # See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
#     self.generation_config = {
#       "temperature": 1,
#       "top_p": 0.95,
#       "top_k": 64,
#       "max_output_tokens": 8192,
#       "response_mime_type": "text/plain",
#     }

#     self.model = genai.GenerativeModel(
#       model_name="gemini-1.5-flash",
#       generation_config=self.generation_config,
#       # safety_settings = Adjust safety settings
#       # See https://ai.google.dev/gemini-api/docs/safety-settings
#     )

#     # TODO Make these files available on the local file system
#     # You may need to update the file paths

#     self.files = [
#       self.upload_to_gemini(f"{ModelAdvisor.PATH}/img1", mime_type="application/octet-stream"),
#       self.upload_to_gemini(f"{ModelAdvisor.PATH}/img2", mime_type="application/octet-stream"),
#       self.upload_to_gemini(f"{ModelAdvisor.PATH}/img3", mime_type="application/octet-stream"),
#       self.upload_to_gemini(f"{ModelAdvisor.PATH}/img4", mime_type="application/octet-stream"),
#       self.upload_to_gemini(f"{ModelAdvisor.PATH}/img5", mime_type="application/octet-stream"),
#       self.upload_to_gemini(f"{ModelAdvisor.PATH}/img6", mime_type="application/octet-stream"),
#       self.upload_to_gemini(f"{ModelAdvisor.PATH}/img7", mime_type="application/octet-stream"),
#       self.upload_to_gemini(f"{ModelAdvisor.PATH}/img8", mime_type="application/octet-stream"),
#     ]

#   def upload_to_gemini(self, path, mime_type=None):
#     """Uploads the given file to Gemini.

#     See https://ai.google.dev/gemini-api/docs/prompting_with_media
#     """
#     file = self.genai.upload_file(path, mime_type=mime_type)
#     print(f"Uploaded file '{file.display_name}' as: {file.uri}")
#     return file

#   def respond(self,input_file):

#     response = self.model.generate_content([
#       "You are part of assitive technology module. Your aim is to analyze image and find ui components marked with numbers in the pircutre. List them with one possible action user can do to them or theirs description or marked word/text. You have to be as descriptive as possible but have very short limit of words. If there is no image, then provide \"NONE\". Do not list more than five. ",
#       self.files[0],
#       "​",
#       "output: 0.  copy word tone \n1.  copy word instruction\n2. copy word mode\n3. copy word the\n4. copy word for\n5. copy word and",
#       "You are part of assitive technology module. Your aim is to analyze image and find ui components marked with numbers in the pircutre. List them with one possible action user can do to them or theirs description or marked word/text. You have to be as descriptive as possible but have very short limit of words. If there is no image, then provide \"NONE\". Do not list more than five. ",
#       self.files[1],
#       "​",
#       "output: 0. Press discourse\n1.  Press gemini\n2. Press gemini\n3. Press prompt \n4. Press prompt \n5. press Documenation",
#       "You are part of assitive technology module. Your aim is to analyze image and find ui components marked with numbers in the pircutre. List them with one possible action user can do to them or theirs description or marked word/text. You have to be as descriptive as possible but have very short limit of words. If there is no image, then provide \"NONE\". Do not list more than five. ",
#       self.files[2],
#       "​",
#       "output: 0. Press Advanced\n1. Press down arrow to open Advanced settings\n2. Press edit safe setting\n3. Press Edit\n4. Press Safety\n5. Press Shield Icon",
#       "You are part of assitive technology module. Your aim is to analyze image and find ui components marked with numbers in the pircutre. List them with one possible action user can do to them or theirs description or marked word/text. You have to be as descriptive as possible but have very short limit of words. If there is no image, then provide \"NONE\". Do not list more than five. ",
#       self.files[3],
#       "​",
#       "output: 0. Press right arrow\n1. Press Circle icon",
#       "You are part of assitive technology module. Your aim is to analyze image and find ui components marked with numbers in the pircutre. List them with one possible action user can do to them or theirs description or marked word/text. You have to be as descriptive as possible but have very short limit of words. If there is no image, then provide \"NONE\". Do not list more than five. ",
#       self.files[4],
#       "​",
#       "output: 0. Open Windows PowerShell\n1. Press up arrow\n2. Press sort button\n3. press view\n4. Press trash can icon\n5. Press folder icon",
#       "You are part of assitive technology module. Your aim is to analyze image and find ui components marked with numbers in the pircutre. List them with one possible action user can do to them or theirs description or marked word/text. You have to be as descriptive as possible but have very short limit of words. If there is no image, then provide \"NONE\". Do not list more than five. ",
#       self.files[5],
#       "​",
#       "output: 0. Copy word cloud\n1. copy word you\n2. copy word more \n3. copy word share\n4. copy word single \n5. copy word file",
#       "You are part of assitive technology module. Your aim is to analyze image and find ui components marked with numbers in the pircutre. List them with one possible action user can do to them or theirs description or marked word/text. You have to be as descriptive as possible but have very short limit of words. If there is no image, then provide \"NONE\". Do not list more than five. ",
#       self.files[6],
#       "​",
#       "output: 0. Open .git\n1. Open Documents\n2. Open Downloads\n3. Open dist\n4. Open build\n5. Open Downloads",
#       "You are part of assitive technology module. Your aim is to analyze image and find ui components marked with numbers in the pircutre. List them with one possible action user can do to them or theirs description or marked word/text. You have to be as descriptive as possible but have very short limit of words. If there is no image, then provide \"NONE\". Do not list more than five. ",
#       self.files[7],
#       "​",
#       "output: 0. Open dist folder\n1. Open build folder \n2. Open Desktop\n3. Open app folder\n4. Open app folder\n5. Open _tmp folder",
#       "You are part of assitive technology module. Your aim is to analyze image and find ui components marked with numbers in the pircutre. List them with one possible action user can do to them or theirs description or marked word/text. You have to be as descriptive as possible but have very short limit of words. If there is no image, then provide \"NONE\". Do not list more than five. ",
#       self.upload_to_gemini(input_file, mime_type="application/octet-stream"),
#       "​",
#     ])

#     return response


