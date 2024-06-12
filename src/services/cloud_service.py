import asyncio

from cloudinary import uploader
import cloudinary
from cloudinary.exceptions import Error as CloudinaryError
from fastapi import HTTPException
from requests import TooManyRedirects
from requests.exceptions import RequestException, Timeout, HTTPError

from src.conf.config import config

cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
)


class CloudService:
    @staticmethod
    def handle_exceptions(err):
        """
        The handle_exceptions function is a custom exception handler that will catch any exceptions
        that are raised by the cloudinary_upload function and return an appropriate HTTP response.
        This allows us to handle errors in a consistent way across our application.

        :param err: Catch the error that is raised by the function
        :return: An http exception
        """
        if isinstance(err, CloudinaryError):
            raise HTTPException(status_code=500, detail=f"Cloudinary API error: {err}")
        elif isinstance(err, RequestException):
            raise HTTPException(status_code=500, detail=f"Ops something get wrong: {err}")
        elif isinstance(err, Timeout):
            raise HTTPException(status_code=500, detail=f"Request timed out: {err}")
        elif isinstance(err, TooManyRedirects):
            raise HTTPException(status_code=500, detail=f"Too many redirects: {err}")
        elif isinstance(err, HTTPError):
            if err.response.status_code == 401:
                raise HTTPException(status_code=401, detail=f"Unauthorized: {err}")
            elif err.response.status_code == 400:
                raise HTTPException(status_code=400, detail=f"Bad request: {err}")
            else:
                raise HTTPException(status_code=500, detail=f"HTTP error: {err}")
        elif isinstance(err, IOError):
            raise HTTPException(status_code=500, detail=f"I/O error: {err}")
        elif isinstance(err, FileNotFoundError):
            raise HTTPException(status_code=404, detail=f"File not found: {err}")
        else:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {err}")

    @staticmethod
    async def upload_image(image_file: bytes, folder_path: str = None):
        """
        The upload_image function uploads an image to the cloudinary server.

        :param image_file: bytes: Bytes object representing the image file
        :param folder_path: str: Specify the folder in which the image will be uploaded to
        :return: A tuple of the image url and public_id
        """
        try:
            response = await asyncio.to_thread(cloudinary.uploader.upload, image_file,
                                               folder=f"ParkSense-AI/{folder_path}")  # type: ignore
            return response['url'], response['public_id']

        except Exception as err:
            CloudService.handle_exceptions(err)

    @staticmethod
    async def delete_image(cloudinary_public_id: str):
        """
        The delete_image function is used to delete a picture from the Cloudinary cloud storage service.
            It takes in one parameter, public_id, which is the unique identifier of the image that will be deleted.
            The function uses asyncio and cloudinary to delete an image with a given public_id.

        :param cloudinary_public_id: str: Identify the picture to be deleted
        :return: A dictionary with the following keys:
        """
        try:
            await asyncio.to_thread(cloudinary.uploader.destroy, cloudinary_public_id)
        except Exception as err:
            CloudService.handle_exceptions(err)

    @staticmethod
    async def update_image_on_cloudinary(cloudinary_public_id: str, params_of_transform: dict):
        """
        The update_image_on_cloudinary function is used to update an image on Cloudinary.
            It takes in a cloudinary_public_id and params_of_transform as arguments, and returns the url of the transformed image.
            The function uses asyncio to run the cloudinary uploader explicit method in a thread, which updates an existing
            resource with new parameters (eager transformation). If successful, it returns the eager transformed url.

        :param cloudinary_public_id: str: Identify the image in cloudinary
        :param params_of_transform: dict: Specify the transformation parameters
        :return: The url of the transformed image
        """
        try:
            response = await asyncio.to_thread(cloudinary.uploader.explicit, cloudinary_public_id,
                                               type='upload', eager=[params_of_transform])  # noqa

            if 'eager' in response and response['eager']:
                eager_transformed_url = response['eager'][0]['url']
                return eager_transformed_url

        except Exception as err:
            CloudService.handle_exceptions(err)


cloud_service = CloudService()
