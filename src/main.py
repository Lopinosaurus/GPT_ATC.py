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
messages=[{"role":"system", "content":"I want you to act like an air traffic controller. Your answers should be concise and precise. You only have to use the real aeronautical language of an air traffic controller, you don't necessarily need to be polite, you have to give me directions so that I can fly. I will talk to you and you will answer me in English. I will give you details of my departure and arrival airport (runways in service, taxiway, weather conditions). I want you to answer me based on this information that you will remember. You will be careful not to confuse the runways and taxiways of the 2 airports (departures and arrivals). A runway is reachable only by one point, so you must indicate only one when the pilot wants to taxi to a runway."}]



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


def check_icao(icao: str):
    """
    Checks if the inputed ICAOs are presents in current data set.
    """
    file = open("airports/airports.json", 'r+', encoding="utf-8")
    airports = json.load(file)['airports']
    is_present = False
    index = -1
    for i in range(len(airports)):
        try:
            if icao.upper() in airports[i]['icao']:
                is_present = True
        except:
            pass
    if not is_present:
        print("The specified airport cannot be found in current database. You can add it (highly recommended) or just indicate to ATC your current airport (will generate more confused ATC answers)")
    file.close()
    return (is_present, index)
    

def main() -> None:
    """
    Launch speech recognition then GPT3.5 requests
    """
    file = open("airports/airports.json", 'r+', encoding="utf-8")
    airports = json.load(file)['airports']
    departure = input("Enter departure ICAO : ")
    arrival = input("Enter arrival ICAO : ")
    (check_d, index_d) = check_icao(departure)
    (check_a, index_a) = check_icao(arrival)
    
    messages.append({"role":"system", "content":"The pilot will take of from " + departure + " and will fly to " + arrival})

    if check_d:
        for i in range(len(airports[index_d]['runways'])):
            messages.append({"role":"system", "content":"A runway on service at the departure airport is the runway " + airports[index_d]['runways'][i]["id"] + " reachable by points " + airports[index_d]['runways'][i]['points']})
    
    if check_a:
        for i in range(len(airports[index_a]['runways'])):
            messages.append({"role":"system", "content":"A runway on service at the arrival airport is the runway " + airports[index_a]['runways'][i]["id"] + " reachable by points" + airports[index_a]['runways'][i]['points']})
        

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
