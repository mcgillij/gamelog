import xmltodict
import json



def xml_to_json(xml_file):
    with open(xml_file) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
        xml_file.close()
        json_data = json.dumps(data_dict, indent=4, ensure_ascii=False)
        return json_data


if __name__ == "__main__":
    xml_file = "games.xml"
    json_data = xml_to_json(xml_file)
    print(json_data)
