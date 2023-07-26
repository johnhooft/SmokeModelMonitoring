from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json

secrets = json.load(open("secrets.json"))

def upload_image(client, image_path, channel, message):
    try:
        response = client.files_upload(
            file=image_path,
            initial_comment=message,
            channels=channel
        )
        return response["file"]["url_private"]
    except SlackApiError as e:
        print(f"Failed to upload image: {e.response['error']}")
        return None

def send_slack_message_with_image(token, channel, message, image_path):
    client = WebClient(token=token)

    # Upload the image and get the private URL
    image_url = upload_image(client, image_path, channel, message)

    if not image_url:
        print("Image upload failed. Aborting.")
        return

def message_format(metadata):
    text = ''
    text += 'Timestamp: ' + str(metadata[0]) + '\n'
    if metadata[1]: text += 'Camera site: Bear Mtn\n'
    else: text += 'Camera site: Prairie\n'
    if metadata[2]: text += 'Fire detected.\n'
    else: text += 'No fire detected.\n'

    return text


def sendtoslack(image_path, metadata):
    # Replace these values with your own:
    slack_token = secrets["token"]
    channel_name = "#smoke-model-monitoring-testing"  # Channel or user ID (e.g., "#general" or "@username")
    message_text = message_format(metadata)
    image_file_path = image_path

    print(message_text)

    send_slack_message_with_image(slack_token, channel_name, message_text, image_file_path)
