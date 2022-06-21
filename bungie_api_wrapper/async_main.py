import os
import asyncio
import json
import time
import logging
import datetime

from dotenv import load_dotenv

from bungie_api_wrapper import BAPI
from custom_logging import CustomFormatter
from bungie_api_wrapper.manifest import Manifest

load_dotenv()

formatter = CustomFormatter()
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger = logging.getLogger('bungie_wrapper')
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)

API_KEY = os.getenv('BUNGIE_API_KEY')

async def get_characters(name, code, platform):
    """Return characters information in hash values.
    
    Function will return all information about User characters in hash values.
    Returned dictionary is ready to be decoded in Destiny manifest.
    
    Args:
        name (str): Bungie user name, ex 'TestUser'.
        code (int): Bungie user code, ex '1234'.
        platform (int): Destiny2 membershipType.
        
    Returns:
        characters_informations (dict): Informations about characters in hash
        values.
    """

    destiny = BAPI(API_KEY)
    characters_informations = {}
    
    # get user membershipId from API request
    destiny_membership_id = await destiny.api.post_search_destiny_player(
        platform, {'displayName': name, 'displayNameCode': code}
    )
    destiny_membership_id = destiny_membership_id['Response'][0]['membershipId']

    # get user profile from API request
    profile = await destiny.api.get_destiny_profile(destiny_membership_id,
                                                    3, [100, 200, 205])
    
    characters_ids = profile['Response']['profile']['data']['characterIds']
    
    async def character(profile, character_id):
        """Add character information in hash values to characters dictionary.
        
        Function will add all informations about single character in hash values,
        to characters dictionary. Using this function we can request character
        endpoint in the same time.
        
        Args:
            profile (dict): Informations about Bungie user profile.
            character_id (str): Destiny2 user Character ID.
        """
        
        char_data = profile['Response']['characters']['data'][character_id]
        items_data = profile['Response']['characterEquipment']['data'] \
            [character_id]['items']
        
        items = {}
        no_weapon_buckets = ['284967655', '1107761855', '1506418338', '2025709351',
                            '3683254069', '4023194814', '4292445962', '4274335291',
                            '3284755031']
        
        for i in range(len(items_data)):
            item = items_data
            try:
                if not str(item[i]['bucketHash']) in no_weapon_buckets:
                    item_raw_data = {}
                    item_resp = await destiny.api.get_item(destiny_membership_id,
                                                           item[i]['itemInstanceId'],
                                                           3, [302, 304, 307])
                    
                    i_hash = item_resp['Response']['item']['data']['itemHash']
                    b_hash = item_resp['Response']['item']['data']['bucketHash']
                    
                    common_data = {
                        'itemHash': i_hash,
                        'bucketHash': b_hash
                    }
                    
                    item_stats = item_resp['Response']['stats']['data']['stats']
                    item_perks = item_resp['Response']['perks']['data']['perks']
                    
                    item_raw_data['common_data'] = common_data
                    item_raw_data['stats'] = item_stats
                    item_raw_data['perks'] = item_perks
                    
                    items[b_hash] = item_raw_data
            except KeyError as k_error:
                logger.error(f'{k_error} Bucket: {item[i]["bucketHash"]} \
                      Item: {item[i]["itemHash"]} Class: {char_data["classHash"]} \
                          ItemInstanceId: {item[i]["itemInstanceId"]}')
                
        characters_informations[char_data['classHash']] = {
            'dateLastPlayed': char_data['dateLastPlayed'],
            'emblemBackgroundPath': char_data['emblemBackgroundPath'],
            'emblemHash': char_data['emblemHash'],
            'emblemPath': char_data['emblemPath'],
            'light': char_data['light'],
            'minutesPlayedTotal': char_data['minutesPlayedTotal'],
            'raceHash': char_data['raceHash'],
            'stats': char_data['stats'],
            'items': items
        }
    
    # in python 3.10.2 this should be replaced with match case
    if len(characters_ids) == 3:
        await asyncio.gather(
            character(profile, characters_ids[0]),
            character(profile, characters_ids[1]),
            character(profile, characters_ids[2])
        )    
    elif len(characters_ids) == 2:
        await asyncio.gather(
            character(profile, characters_ids[0]),
            character(profile, characters_ids[1])
        )
    elif len(characters_ids) == 1:
        await asyncio.gather(
            character(profile, characters_ids[0])
        )
    
    await destiny.close()
    with open('characters.json', 'w') as file:
        json.dump(characters_informations, indent=2, sort_keys=True, fp=file)
    return characters_informations

async def get_clan_informations(group_id: int):
    destiny = BAPI(API_KEY)
    
    response = await destiny.api.get_clan(group_id)
    response = response['Response']
    members_list = await get_clan_members(group_id)
    await destiny.close()
    
    creation_date = response['detail']['creationDate'].replace("T", " ").replace("Z", "")
    avatar_path_url = 'https://www.bungie.net/' + response['detail']['avatarPath']
    
    informations = {
        'name': response['detail']['name'],
        'about': f"{response['detail']['about']}",
        'callsign': response['detail']['clanInfo']['clanCallsign'],
        'motto': response['detail']['motto'],
        'clan_icon_url': avatar_path_url,
        'founder': response['founder']['bungieNetUserInfo']['supplementalDisplayName'],
        'members_list': members_list,
        'members_count': response['detail']['memberCount'],
        'creation_date': creation_date,
        'exp': response['detail']['clanInfo']['d2ClanProgressions']['584850370'] \
            ['currentProgress'],
        'level':  response['detail']['clanInfo']['d2ClanProgressions']['584850370'] \
            ['level'],
        'level_cap':  response['detail']['clanInfo']['d2ClanProgressions']['584850370'] \
            ['levelCap']
    }
     
    return informations
    
async def get_clan_members(group_id):
    destiny = BAPI(API_KEY)
    members_list = []
    
    response = await destiny.api.get_destiny_clan_members(group_id)
    response = response['Response']['results']
    try:
        for x in response:
            try:
                name = x['bungieNetUserInfo']['bungieGlobalDisplayName']
                code = x['bungieNetUserInfo']['bungieGlobalDisplayNameCode']
                if not name:
                    pass
                else:
                    member = f'{name}#{code}'
                    members_list.append(member)   
            except KeyError as k_error:
                logger.error(k_error)
    except KeyError as error:
        logger.error(error)
    
    await destiny.close()
    return members_list

async def get_destiny_clan_weekly_rewards(group_id):
    destiny = BAPI(API_KEY)
    clan_weekly_rewards = {}
    
    response = await destiny.api.get_clan_weekly_reward(group_id)
    response = response['Response']['rewards'][0]['entries']
    
    try:
        for rewards in response:
            if rewards['rewardEntryHash'] == 3789021730:
                clan_weekly_rewards['Nightfall Strikes'] = rewards['earned']
            elif rewards['rewardEntryHash'] == 248695599:
                clan_weekly_rewards['Gambit'] = rewards['earned']
            elif rewards['rewardEntryHash'] == 2043403989:
                clan_weekly_rewards['Raids'] = rewards['earned']
            elif rewards['rewardEntryHash'] == 964120289:
                clan_weekly_rewards['Rumble'] = rewards['earned']
    except KeyError as key_error:
        logger.error(key_error)
    except ValueError as value_error:
        logger.error(value_error)
    
    await destiny.close()
    return clan_weekly_rewards

async def get_character_history(platform, destiny_membership_id, character_id,
                                count=10, mode=None, page=0):
    destiny = BAPI(API_KEY)
    manifest = Manifest()
    
    character_history = destiny.api.get_activity_history(platform, destiny_membership_id,
                                                         character_id, count, mode, page)
    
    
async def get_character_history_test(name, code, platform, count=5, mode=None, page=0):
    destiny = BAPI(API_KEY)
    manifest = Manifest()
    
    destiny_membership_id = await destiny.api.post_search_destiny_player(
        platform, {'displayName': name, 'displayNameCode': code}
    )
    destiny_membership_id = destiny_membership_id['Response'][0]['membershipId']
    
    profile = await destiny.api.get_destiny_profile(destiny_membership_id, 3, [200])
    profile = profile['Response']['characters']['data']
    
    characters = {}
    try:
        for character_id, character_data in profile.items():
            characters[character_id] = character_data['classHash']
    except Exception as error:
        print(error)
        
    characters_history = {}
    
    try:
        for character_id, character_hash in characters.items():
            activities = {}
            class_name = manifest.decode_character_class(character_hash)
            char_history = await destiny.api.get_activity_history(platform, destiny_membership_id,
                                                                character_id, count, mode, page)
            for activ in char_history['Response']['activities']:
                activity = manifest.decode_activity_name(activ['activityDetails']['directorActivityHash'])
                activity_period = activ['period'].replace('T', ' ').replace('Z', '')
                activity_date = datetime.datetime.strptime(activity_period, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
                activities[activity_date] = {
                    'activity': activity,
                    'modes': activ['activityDetails']['modes'],
                    'duration': activ['values']['activityDurationSeconds']['basic']['displayValue']
                }
            characters_history[class_name] = activities
    except Exception as error:
        print(error)
    
    await destiny.close()
    return characters_history

async def main():
    pass
    
if __name__ == '__main__':
    asyncio.run(main())        
    
