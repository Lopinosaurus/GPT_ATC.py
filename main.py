from speech_recognition import Recognizer, Microphone
import os
import openai
from dotenv import load_dotenv
import asyncio
import edge_tts
import play_wav
import playsound

load_dotenv()
openai.api_key = os.getenv("API_KEY")
messages=[{"role":"system", "content":"Je veux que tu agisses comme un controleur aérien à l'aéroport Bordeaux-Mérignac. Tes réponses doivent être concises et précises, et doivent respecter le plan exact de l'aéroport (numéro de piste et taxiway). Tu dois uniquement utiliser le réel langage aéronautique d'un controleur aérien, tu n'as pas forcément besoin d'être poli, tu dois me donner des indications pour que je puisse piloter. Je te parlerai et tu me répondra en anglais."}]



def get_audio_voice() -> str:
    """
    Uses speech recognition to capture audio user input and returns it as string.
    """
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
            language="en-GB"
        )
        print(text)

    except Exception as exception:
        print("Error : ", exception)

    return text


async def tts_play(rep) -> None:
    """
    Async method to play microsoft tts of GPT3.5 response.
    """
    tts_com = edge_tts.Communicate(rep, "en-GB-SoniaNeural")
    await tts_com.save("voice.mp3")


def main() -> None:
    """
    Launch speech recognition then GPT requests
    """
    user_input = get_audio_voice()
    messages.append({"role":"user", "content":user_input})
    print("Sending request...")

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages 
    )

    gpt_response = completion.choices[0].message.content
    print ("GPT Model configured. ATC Ready.")
    print("ATC : ", gpt_response)
    asyncio.get_event_loop().run_until_complete(tts_play(gpt_response))

    playsound.playsound('voice.mp3')


if __name__ == "__main__":
    main()

# todo :
# rajout d'args dans le cas ou le joueur n'est pas dans les conditions qu'il prentend etre
# arg GPT avec 1 : phrase joueur, 2: contexte du jeu