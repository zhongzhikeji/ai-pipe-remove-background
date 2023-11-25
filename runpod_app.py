from io import BytesIO
import requests
import json
from PIL import ImageOps
from diffusers.utils import load_image
from transparent_background import Remover
import runpod

remover = Remover()

def buff_png (image):
    buff = BytesIO()
    image.save(buff, format = 'PNG')
    buff.seek(0)
    return buff

def upload_image (url, image):
    requests.put(url, data = buff_png(image), headers = { 'Content-Type': 'image/png' })

def webhook_callback (url, data):
    if url.startswith('http'):
        requests.post(url, json = data)

def run (job):
    print('debug', job)

    _input = job.get('input')
    _webhook = job.get('webhook')

    input_url = _input.get('input_url')
    upload_url = _input.get('upload_url')
    get_mask = _input.get('get_mask')
    invert_mask = _input.get('invert_mask')

    # move later
    input_image = load_image(input_url)
    get_mask = 'map' if get_mask else 'rgba'

    output_image = remover.process(
        input_image,
        type = get_mask
    )

    if invert_mask is True:
        output_image = ImageOps.invert(output_image)

    upload_image(upload_url, output_image)

    webhook_callback(_webhook, json.dumps(job))

    return job

runpod.serverless.start({ 'handler': run })
