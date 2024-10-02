from odoo import http
from odoo.http import request
import json
from odoo.exceptions import AccessError
import mimetypes
from odoo.addons.web.controllers.webmanifest import WebManifest
from odoo.tools import ustr, file_open


class CustomWebManifest(WebManifest):

    def _icon_path(self):
        return "new_logo_for_pwa/static/img/odoo-icon-192x192.png"

    @http.route(
        "/web/manifest.webmanifest", type="http", auth="public", methods=["GET"]
    )
    def webmanifest(self):
        """Returns a WebManifest describing the metadata associated with a web application.
        Using this metadata, user agents can provide developers with means to create user
        experiences that are more comparable to that of a native application.
        """
        web_app_name = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("web.web_app_name", "Odoo")
        )
        manifest = {
            "name": "DashBoard 2",
            "short_name": "DashBoard 2",
            "start_url": "/",
            "scope": "/",
            "display": "standalone",
            "description": "Ваш бізнес на новій платформі",
            "background_color": "#006AFF",
            "theme_color": "#006AFF",
            "lang": "uk",
            "prefer_related_applications": False,
            "related_applications": [
                {"platform": "web"},
                {
                    "platform": "play",
                    "url": "https://play.google.com/store/apps/details?id=cheeaun.hackerweb",
                },
            ],
        }
        icon_sizes = [
            "48x48",
            "72x72",
            "96x96",
            "128x128",
            "144x144",
            "192x192",
            "284x284",
            "512x512",
        ]
        manifest["icons"] = [
            {
                "src": "/new_logo_for_pwa/static/img/odoo-icon-%s.png" % size,
                "sizes": size,
                "type": "image/png",
            }
            for size in icon_sizes
        ]
        manifest["shortcuts"] = self._get_shortcuts()
        body = json.dumps(manifest, default=ustr)
        response = request.make_response(
            body,
            [
                ("Content-Type", "application/manifest+json"),
            ],
        )
        return response
