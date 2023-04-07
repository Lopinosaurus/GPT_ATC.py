from speech_recognition import Recognizer, Microphone
import json
import os
import openai
from dotenv import load_dotenv
import asyncio
import edge_tts
import playsound
import keyboard

load_dotenv()
openai.api_key = os.getenv("API_KEY")

# Properties definition
messages=[{"role":"system", "content":"Je veux que tu agisses comme un controleur aérien. Tes réponses doivent être concises et précises. Tu dois uniquement utiliser le réel langage aéronautique d'un controleur aérien, tu n'as pas forcément besoin d'être poli, tu dois me donner des indications pour que je puisse piloter. Je te parlerai et tu me répondra en anglais. Je vais te donner des détails de mon aéroport de départ et d'arrivé (pistes en services, taxiway, conditions météorologiques). Je veux que tu me réponde en fonction de ces informations que tu garderas en mémoire."}]
departure_icao = None
arrival_icao = None



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


async def tts_play(rep: str) -> None:
    """
    Async method to play microsoft tts of GPT3.5 response.
    """
    tts_com = edge_tts.Communicate(rep, "en-GB-SoniaNeural")
    await tts_com.save("voice.mp3")


def check_icao(icao: str) -> bool:
    """
    Checks if the inputed ICAOs are presents in current data set.
    """
    file = open("../airports/airports.json", 'r+', encoding="utf-8")
    airports = json.load(file)
    is_present = False
    for ap in airports:
        if icao in ap['icao']:
            is_present = True
    if not is_present:
        print("The specified airport cannot be found in current database. You can add it (highly recommended) or just indicate to ATC your current airport (will generate more confused ATC answers)")
    file.close()
    return is_present
    

def main() -> None:
    """
    Launch speech recognition then GPT3.5 requests
    """
    file = open("../airports/airports.json", 'r+', encoding="utf-8")
    airports = json.load(file)
    departure = input("Enter departure ICAO : ")
    arrival = input("Enter arrival ICAO : ")
    check_d = check_icao(departure)
    check_a = check_icao(arrival)
    
    #if check_d:
        # message.append All infos
    # if check_a:
        # message.append All infos
        
    
    print("GPT_ATC.py ready. Press k to talk to ATC.")
    while True:
        if keyboard.is_pressed('k'):
            print("Recording...")
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
            os.remove("voice.mp3")
            print("Press K to talk to ATC.")


if __name__ == "__main__":
    main()
