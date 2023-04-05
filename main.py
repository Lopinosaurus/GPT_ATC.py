from speech_recognition import Recognizer, Microphone
import pyttsx3
import os
import openai
import time

openai.api_key = os.getenv("API_KEY")

def get_audio_voice():
    recognizer = Recognizer()

    with Microphone() as source:
        print("Setting up audio source...")
        recognizer.adjust_for_ambient_noise(source)
        print("Please talk :")
        record = recognizer.listen(source)
        print("Record received.")


    try:
        print("Voice Input: ")
        text = recognizer.recognize_google(
            record,
            language="fr-FR"
        )
        print(text)

    except Exception as exception:
        print("Error : ", exception)

    return text


messages=[{"role":"system", "content":"You are an air controller. Your answer must be concise and precise. You must talk with actual air traffic control vocabulary. No need to be polite, as you just need to give me directive to allow me to fly me aircraft safely."}]
#messages.append({"role":"user", "content": get_audio_voice()})

user_input = get_audio_voice()
print("Thinking...")
engine = pyttsx3.init()

completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages 
)

gpt_response = completion.choices[0].message.content
engine.say(gpt_response)
engine.runAndWait()

# todo :
# rajout d'args dans le cas ou le joueur n'est pas dans les conditions qu'il prentend etre
# arg GPT avec 1 : phrase joueur, 2: contexte du jeu