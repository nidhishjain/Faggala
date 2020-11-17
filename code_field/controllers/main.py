# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################



import babel.messages.pofile
import base64
import copy
import datetime
import functools
import glob
import hashlib
import io
import itertools
import jinja2
import json
import logging
import operator
import os
import re
import sys
import tempfile
import time

import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from collections import OrderedDict, defaultdict, Counter
from werkzeug.urls import url_decode, iri_to_uri
from lxml import etree
import unicodedata


import odoo
import odoo.modules.registry
from odoo.api import call_kw, Environment
from odoo.modules import get_module_path, get_resource_path
from odoo.tools import image_process, topological_sort, html_escape, pycompat, ustr, apply_inheritance_specs, lazy_property
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools.translate import _
from odoo.tools.misc import str2bool, xlsxwriter, file_open
from odoo.tools.safe_eval import safe_eval
from odoo import http, tools
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception, Response
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.models import check_method_name
from odoo.service import db, security



from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import CSVExport
from odoo.addons.web.controllers.main import ExportFormat , ExcelExport, ExportXlsxWriter


class InheritCSVExport(CSVExport):

    def from_data(self, fields, rows):
        fp = io.BytesIO()
        writer = pycompat.csv_writer(fp, quoting=1)

        for f in fields:
            if f.find('/الاسم') != -1:
                no = fields.index(f)
                fields[no]= '\n تسلسل عناصر قائمة الاسعار  \n'
                fields.insert(no + 1, '\n اسماء عناصر قائمة الاسعار \n')
                print(f)


        writer.writerow(fields)

        for data in rows:
            row = []
            for d in data:
                # Spreadsheet apps tend to detect formulas on leading =, + and -
                if isinstance(d, str) and d.startswith(('=', '-', '+')):
                    d = "'" + d
                if isinstance(d, str) and d.find('Product: [') != -1:
                    d1 = d.split('[')[1].split(']')[0]
                    d = d.split('[')[1].split(']')[1]
                    row.append(pycompat.to_text(d1))

                row.append(pycompat.to_text(d))
            writer.writerow(row)

        return fp.getvalue()


class InhertExcelExport(ExcelExport):

    def from_data(self, fields, rows):

        try:
            no = fields.index('المنتج')
            fields[no] = ' تسلسل المنتج  '
            fields.insert(no + 1, 'اسم المنتج ')
        except:
            print("not product")

        try:
            no = fields.index('عناصر قائمة الأسعار/الاسم')
            fields[no] = ' تسلسل عناصر قائمة الاسعار  '
            fields.insert(no + 1, 'اسماء عناصر قائمة الاسعار ')
        except:
             print("not name")

        with ExportXlsxWriter(fields, len(rows)) as xlsx_writer:
            for row_index, row in enumerate(rows):
                for cell_index, cell_value in enumerate(row):
                    if isinstance(cell_value, (list, tuple)):
                        cell_value = pycompat.to_text(cell_value)

                    if isinstance(cell_value, str) and cell_value.find('Product: [') != -1:
                        rows[row_index].insert(cell_index + 1, cell_value.split('[')[1].split(']')[1])
                        cell_value = cell_value.split('[')[1].split(']')[0]

                    if isinstance(cell_value, str) and cell_value.find('[') != -1 and cell_value.split('[')[1].split(']')[0].isnumeric():
                        rows[row_index].insert(cell_index+1,cell_value.split('[')[1].split(']')[1])
                        cell_value = cell_value.split('[')[1].split(']')[0]

                    xlsx_writer.write_cell(row_index + 1, cell_index, cell_value)

        return xlsx_writer.value