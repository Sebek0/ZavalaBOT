import os
import asyncio
import json
import time
import sys

from dotenv import load_dotenv

from bungie_api_wrapper import BAPI

load_dotenv()

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
                print(f'{k_error} Bucket: {item[i]["bucketHash"]} \
                      Item: {item[i]["itemHash"]} Class: {char_data["classHash"]}')
        
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

async def get_clan_members(group_id):
    destiny = BAPI(API_KEY)
    members_list = []
    
    response = await destiny.api.get_destiny_clan_members(group_id)
    response = response['Response']['results']
    
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
            print(k_error)
    
    await destiny.close()
    return members_list


async def main():
    await get_characters('sebek.', 6034, 3)sdada
    
if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    start_time = time.time()
    asyncio.run(main())
    print("--- %s seconds ---" % (time.time() - start_time))           