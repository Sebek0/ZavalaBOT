import requests
import json
import os
import urllib

from dotenv import load_dotenv


class Manifest:
    def __init__(self) -> None:
        load_dotenv()
        self.manifest_url = os.getenv('MANIFEST_URL')
        self.api_key = os.getenv('BUNGIE_API_KEY')
        
    def check_manifest(self):
        """Check manifest files and manifest version.
        
        Function is checking if directiory with essential manifest files exists.
        If not it will create new directory and save new files there. If directory
        already exists function will check if version saved on machine is the same
        in Bungie API. If not it will update outdated version.
        """
        
        if not os.path.isdir(r'bungie_api_wrapper/Manifest'):
            self.get_manifest_files()
        else:
            get_manifest = requests.get(self.manifest_url)
            manifest_data = get_manifest.json()
            with open(r'bungie_api_wrapper/Manifest/version.json') as v_file:
                version_data = json.load(v_file)
                version = version_data['version']
            if version != str(manifest_data['Response']['version']):
                print('Manifest version is outdated! Downloading new version...')
                self.get_manifest_files()
                if os.path.isfile(r'bungie_api_wrapper/Manifest/version.json'):
                    print('Downloading complete, version is up to date.')
                else:
                    print('Unexpected error while downloading new version!')
            else:
                print('Manifest version is up to date!')
    
    def get_manifest_files(self):
        """Check manifest directory."""
        
        def download_manifest_files():
            """Download and save manifest definitions files."""
            
            headers = {'X-API-Key': str(self.api_key)}
            get_manifest = requests.get(url=self.manifest_url, headers=headers)
            
            manifest_data = get_manifest.json()
            definition_keys = ['DestinyInventoryItemDefinition',
                                'DestinyInventoryBucketDefinition',
                                'DestinyDamageTypeDefinition',
                                'DestinyStatDefinition',
                                'DestinySandboxPerkDefinition',
                                'DestinyClassDefinition',
                                'DestinyRaceDefinition']
            
            for definition in definition_keys:
                download_manifest_url = 'http://www.bungie.net' + \
                    manifest_data['Response']['jsonWorldComponentContentPaths']['en'] \
                        [definition]
                response = requests.get(download_manifest_url)
                json_data = json.loads(response.text)
                with open(rf'bungie_api_wrapper/Manifest/{definition}.json', 'w') as j_file:
                    json.dump(json_data, fp=j_file)
            
            version = manifest_data['Response']['version']
            with open(r'bungie_api_wrapper/Manifest/version.json', 'w') as v_file:
                json.dump({'version': version}, fp=v_file)
        
        if not os.path.isdir(r'bungie_api_wrapper/Manifest'):
            os.mkdir(r'bungie_api_wrapper/Manifest/')
            download_manifest_files()
        else:
            download_manifest_files()
            
    def decode_characters_from_manifest(self, characters_data: dict) -> dict:
        """Decode all characters informations using manifest json files.
        
        Function is using multiple json files requested from Bungie API endpoint,
        to decode character, items, hashes and create new decoded dictionary.
        
        Args:
            characters_data (dict): Destiny2 characters hash values.
        
        Returns:
            characters (dict): Decoded hash values from characters_data.
        """
        
        characters = {}
        try:
            # Class manifest file
            with open(r'bungie_api_wrapper/Manifest/DestinyClassDefinition.json') as class_man:
                class_manifest = json.load(class_man)
            # Race manifest file
            with open(r'bungie_api_wrapper/Manifest/DestinyRaceDefinition.json') as race_man:
                race_manifest = json.load(race_man)
            # Items manifest file
            with open(r'bungie_api_wrapper/Manifest/DestinyInventoryItemDefinition.json') as item_man:
                item_manifest = json.load(item_man)
            # Bucket manifest file
            with open(r'bungie_api_wrapper/Manifest/DestinyInventoryBucketDefinition.json') as bucket_man:
                bucket_manifest = json.load(bucket_man)
            # Item stats manifest file
            with open(r'bungie_api_wrapper/Manifest/DestinyStatDefinition.json') as stat_man:
                stat_manifest = json.load(stat_man)
            # Damage type manifest file
            with open(r'bungie_api_wrapper/Manifest/DestinyDamageTypeDefinition.json') as damage_man:
                damage_manifest = json.load(damage_man)
            # Item perks manifest file
            with open(r'bungie_api_wrapper/Manifest/DestinySandboxPerkDefinition.json') as perk_man:
                perk_manifest = json.load(perk_man) 

            for character in characters_data.keys():

                class_name = class_manifest[str(character)]['displayProperties']['name']
                
                race_hash = characters_data[character]['raceHash']
                race_name = race_manifest[str(race_hash)]['displayProperties']['name']
                
                emblem_hash = characters_data[character]['emblemHash']
                emblem_name = item_manifest[str(emblem_hash)]['displayProperties']['name']
                character_stat = {}
                for s_hash, s_value in characters_data[character]['stats'].items():
                    stat_name = stat_manifest[s_hash]['displayProperties']['name']
                    
                    character_stat[stat_name] = s_value
            
                items_details = {}
                for v in characters_data[character]['items'].values():
                    item_hash = str(v['common_data']['itemHash'])
                    
                    item_name = item_manifest[item_hash]['displayProperties']['name']
                    item_icon = item_manifest[item_hash]['displayProperties']['icon']
                    if not 'iconWatermark' in item_manifest[item_hash].keys():
                        item_watermark = None
                    else:
                        item_watermark = item_manifest[item_hash]['iconWatermark']
                    
                    
                    bucket_hash = str(v['common_data']['bucketHash'])
                    bucket_name = bucket_manifest[bucket_hash]['displayProperties']['name']
                
                    item_stats = {}
                    for stat in v['stats'].values():
                        stat_hash = str(stat['statHash'])
                        stat_value = str(stat['value'])
                        
                        if not 'icon' in stat_manifest[stat_hash]['displayProperties'].keys():
                            stat_name = stat_manifest[stat_hash]['displayProperties']['name']
                            stat_icon = None
                        else:
                            stat_name = stat_manifest[stat_hash]['displayProperties']['name']
                            stat_icon = stat_manifest[stat_hash]['displayProperties']['icon']
                        
                        item_stats[stat_name] = {
                            'value': stat_value,
                            'icon': stat_icon
                        }
                    
                    item_perks = {}
                    for perk in v['perks']:
                        perk_hash = str(perk['perkHash'])
                        perk_data = perk_manifest[perk_hash]
                        
                        if perk_data['damageType'] != 0:
                            dmg_type_hash = str(perk_data['damageTypeHash'])
                            dmg_type = damage_manifest[dmg_type_hash]
                            dmg_type_name = dmg_type['displayProperties']['name']
                            dmg_type_icon = dmg_type['displayProperties']['icon']
                            
                            item_perks['damage_type'] = {
                                'name': dmg_type_name,
                                'icon': dmg_type_icon
                            }
                        elif perk_data['isDisplayable'] is True:
                            perk_name = perk_data['displayProperties']['name']
                            perk_icon = perk_data['displayProperties']['icon']

                            item_perks[perk_name] = {
                                'name': perk_name,
                                'icon': perk_icon
                            }
                    items_details[bucket_name] = {
                        'common_data': {
                            'item_name': item_name,
                            'item_bucket': bucket_name,
                            'item_icon': item_icon,
                            'item_watermark': item_watermark
                        },
                        'perks': item_perks,
                        'stats': item_stats
                    }
                    
                char = characters_data[character]
                characters[class_name] = {
                    'dateLastPlayed': char['dateLastPlayed'],
                    'emblemBackgroundPath': char['emblemBackgroundPath'],
                    'emblemPath': char['emblemPath'],
                    'emblemName': emblem_name,
                    'light': char['light'],
                    'minutesPlayedTotal': char['minutesPlayedTotal'],
                    'raceName': race_name,
                    'stats': character_stat,
                    'items': items_details                        
                    }
        except Exception as error: # write proper Exception handler!
            print(f'Manifest error: {error}')
        
        return characters
    
    def decode_clan_leaderboard_from_manifest(): # will do in future
        pass
    
    # not working for now
    def get_manifest_item(self, common_data: dict, stats: dict, perks: list) -> dict:
        """Decode single weapon and return decoded dictionary.
        
        Args:
            common_data (dict): Common informations about weapon.
            stats (dict): Weapon stats.
            perks (list): Weapon perk list
            
        Returns:
            item_data (dict): Decoded informationsa about weapon.
        """
        
        item_data = {}
        with open('man_data.json') as file:
            manifest_data = json.load(file)
            
        try:
            item_hash = str(common_data['itemHash'])
            item_bucket_hash = str(common_data['bucketHash'])
                      
            item_name = manifest_data['DestinyInventoryItemDefinition'][item_hash] \
                ['displayProperties']['name']
            bucket_name = manifest_data['DestinyInventoryBucketDefinition'] \
                [item_bucket_hash]['displayProperties']['name']
            
            item_stats = {}    
            for value in stats.values():
                stat_hash = str(value['statHash'])
                stat_value = str(value['value'])
                
                stat_name = manifest_data['DestinyStatDefinition'][stat_hash] \
                    ['displayProperties']['name']
                item_stats[stat_name] = stat_value
                
            item_perks = {}    
            for perk in perks:
                perk_hash = str(perk['perkHash'])
                perk_data = manifest_data['DestinySandboxPerkDefinition'][perk_hash]
                
                if perk_data['damageType'] != 0:
                    damage_type_hash = str(perk_data['damageTypeHash'])
                    damage_type = manifest_data['DestinyDamageTypeDefinition'] \
                        [damage_type_hash]['displayProperties']
                    damage_type_name = damage_type['name']
                    damage_type_icon = damage_type['icon']
                    
                    item_perks['damage_type'] = {
                        'name': damage_type_name,
                        'icon': damage_type_icon
                    }
                elif perk_data['isDisplayable'] is True:
                    perk_name = perk_data['displayProperties']['name']
                    perk_icon = perk_data['displayProperties']['icon']

                    item_perks[perk_name] = {
                        'icon': perk_icon
                    }
            
            item_data[item_name] = {
                'bucket': bucket_name,
                'perks': item_perks,
                'stats': item_stats
            }
        except Exception as error:
            print(f'MANIFEST ERROR: {error}')
        return item_data

def main():
    manifest = Manifest()
    manifest.check_manifest()
    print('Done')
    
if __name__ == '__main__':
    main()