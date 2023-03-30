# -*- coding: utf-8 -*-
#################################################################################
# Author      : Bui Vu Minh
#################################################################################
{
  "name"                 :  "Website of AARDWOLF",
  "summary"              :  "It is provide a common form for all filters and attributes inside product grid view.",
  "category"             :  "Website",
  "version"              :  "1.0.1",
  "sequence"             :  1,
  "author"               :  "Bui Vu Minh",
  "license"              :  "",
  "website"              :  "",
  "description"          :  """Website Aardwolf category
                              Customer design for website of AARDWOLF""",
  "depends"              :  ['website','sale','website_sale'],
  "data"                 :  ['views/inherit_website_template.xml',
                             'security/ir.model.access.csv'],
  "demo"                 :  [],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "pre_init_hook"        :  "pre_init_check",
}