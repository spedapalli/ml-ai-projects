from http import client
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse
import api.health_conversation_model_api


client = TestClient(api.health_conversation_model_api.app)

def test_api_sentiment_category():
    long_text:str = '''I'm a teenager, and throughout my entire life, I've never really had good parents, or parents at all for that matter. I'm not exaggerating. I was living with my mom and grandparents until my father, in prison for most of my life, got out when I was in middle school. His mom, my grandma, only lived a mile down the road from my mom’s house, and I was so awe-stricken with my dad that I got to stay with him for a long time. 
    Meanwhile, I did not realize that my mom was doing hardcore drugs. My mom went to prison for that and lost her café. We live in a very small town, so everyone knew about it, and I was bullied because of who my parents were. My dad ended up getting in with the wrong people and went back to prison. My mom and him had a mutual friend and often hung out at that person’s house. 
    My parents did not get along at this point. We were driving him home one day from this house, and my mom stopped the car and kicked him out. He got out of the car, went to the driver’s side, and punched my mom in the face. I got out and told him not to hit my mom. At that point, I was really scared and mad that he did that, so I ran towards him to stop him. He literally picked me up and threw me on the back of a gravel road. 
    I couldn't even walk. My mom tried to help me, but he started choking her. I hobbled over, and she barely got into the car, and we quickly drove away and called the police and ambulance. He was so badly strung out on drugs. He went to prison again and seems to be doing well. I met up with him once with my grandma, and we had coffee, but he's so hard to handle. I think a lot of it is that I can't bring myself to forgive him. 
    My mom went back to prison again for drugs, and while she was in there, I moved in with my dad’s mom (the one who lived just down the road) because I trust her, her house is stable, and she's more nurturing, understanding, and loving then my other grandparents. I also stay at my boyfriend’s a lot. Now that my mom is out of prison, she's trying to control every aspect of my life. 
    She’s trying to make me move back home out of Susan's house, and I don't want to. I don't like it there. They condone drug abuse and many other things, and I'm just not comfortable. She's even threatened to call the police and say I'm a runaway because she has custody of me. My boyfriend has always had this picture-perfect life, and his family are strict Christians. 
    One time, his mom even went as far as to say that if he and I break up, if we were having sex, I would say that he", "raped me. I've got so many problems I don't even know what to do.'''

    senti = client.post("/sentiment_category/", content=long_text)
    print(senti)