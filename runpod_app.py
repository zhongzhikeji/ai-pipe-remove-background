from io import BytesIO
import requests
import json
from PIL import ImageOps
from diffusers.utils import load_image
from transparent_background import Remover
from urllib.parse import urlparse
import runpod

remover = Remover()

def buff_png (image):
    buff = BytesIO()
    image.save(buff, format = 'PNG')
    buff.seek(0)
    return buff

def upload_image (url, image):
    response = requests.put(url, data = buff_png(image), headers = { 'Content-Type': 'image/png' })
    response.raise_for_status()

def webhook_callback (url, data):
    if url.startswith('http'):
        response = requests.post(url, json = data)
        response.raise_for_status()

def extract_origin_pathname (url):
    parsed_url = urlparse(url)
    origin_pathname = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
    return origin_pathname

def run (job):
    # prepare task
    try:
        print('debug', job)

        _input = job.get('input')
        _webhook = job.get('webhook', '')

        input_url = _input.get('input_url')
        upload_url = _input.get('upload_url')
        get_mask = _input.get('get_mask')
        background_color = _input.get('background_color')
        get_overlay = _input.get('get_overlay')
        invert_mask = _input.get('invert_mask')

        # move later
        input_image = load_image(input_url)
        get_mask = 'map' if get_mask else 'rgba'

        if type(background_color) == str:
            get_mask = background_color

        if get_overlay is True:
            get_mask = 'overlay'

        output_image = remover.process(
            input_image,
            type = get_mask
        )

        if background_color is None and get_overlay is None and invert_mask is True:
            output_image = ImageOps.invert(output_image)

        # output
        output_url = extract_origin_pathname(upload_url)
        output = { 'output_url': output_url }

        # payload
        payload = job.copy()
        payload['output'] = output

        upload_image(upload_url, output_image)
        webhook_callback(_webhook, json.dumps(payload))

        return output

    # caught http[s] error
    except requests.exceptions.RequestException as e:
        return { 'error': e.args[0] }

runpod.serverless.start({ 'handler': run })
