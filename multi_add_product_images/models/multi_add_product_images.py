# models/product_image.py
import base64
import zipfile
from io import BytesIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    zip_file = fields.Binary(
        string="Додати фото за допомогою Zip-архiву (1 фото у списку буде головним)"
    )
    zip_filename = fields.Char(string="Zip Filename")
    image_files = fields.Many2many(
        "ir.attachment",
        "product_template_attachment_rel",
        "product_template_id",
        "attachment_id",
        string="Обрати фото для завантаження (1 фото у списку буде головним)",
    )

    @api.model
    def create_images_from_zip(self, zip_data):
        archive = zipfile.ZipFile(BytesIO(base64.b64decode(zip_data)))
        image_obj = self.env["product.image"]

        # Get the list of files and sort by name to keep the order as in a folder
        zip_files = sorted(archive.namelist())
        is_first_image = True  # Flag for main image

        for file_name in zip_files:
            if file_name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                image_data = archive.read(file_name)
                image_record = image_obj.create(
                    {
                        "product_tmpl_id": self.id,
                        "name": file_name, 
                        "image_1920": base64.b64encode(image_data),
                    }
                )
                # The first photo (given the sorting) will be the main photo
                if is_first_image:
                    self.image_1920 = base64.b64encode(image_data)
                    is_first_image = False

    @api.model
    def create_images_from_files(self):
        image_obj = self.env["product.image"]
        is_first_image = True
        for attachment in reversed(self.image_files):
            image_data = attachment.datas
            image_record = image_obj.create(
                {
                    "product_tmpl_id": self.id,
                    "name": attachment.name,
                    "image_1920": image_data,
                }
            )
            if is_first_image:
                self.image_1920 = image_data
                is_first_image = False

    def action_upload_images_from_zip(self):
        if not self.zip_file:
            raise UserError(_("Будь ласка, спочатку завантажте zip-файл."))
        self.create_images_from_zip(self.zip_file)
        self.zip_file = False
        self.zip_filename = False

    def action_upload_images_from_files(self):
        if not self.image_files:
            raise UserError(_("Будь ласка, спочатку виберіть зображення."))
        self.create_images_from_files()
        self.image_files = [(5, 0, 0)]  # Clear the field after uploading

    def action_delete_all_images(self):
        # Delete all images related with product.template
        images = self.env["product.image"].search([("product_tmpl_id", "=", self.id)])
        images.unlink()

        # Delete all attachments
        attachments = self.env["ir.attachment"].search(
            [("res_model", "=", "product.template"), ("res_id", "=", self.id)]
        )
        attachments.unlink()

        # Delete main product image
        self.image_1920 = False

    def action_download_all_images(self):
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            # Add primary image
            if self.image_1920:
                zip_file.writestr(
                    f"{self.name}_main_image.png", base64.b64decode(self.image_1920)
                )

            # Add secondary images
            images = self.env["product.image"].search(
                [("product_tmpl_id", "=", self.id)]
            )
            for image in images:
                if image.image_1920:
                    zip_file.writestr(image.name, base64.b64decode(image.image_1920))

        zip_buffer.seek(0)
        zip_data = zip_buffer.read()
        zip_filename = f"{self.default_code}.zip"

        attachment = self.env["ir.attachment"].create(
            {
                "name": zip_filename,
                "type": "binary",
                "datas": base64.b64encode(zip_data),
                "res_model": self._name,
                "res_id": self.id,
                "mimetype": "application/zip",
            }
        )

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }
