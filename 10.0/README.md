Fictiv Odoo V10.x
======

For Odoo 10 the enterprise modules and the fictiv-odoo code are in 2 different locations. This will be true for pretty much any version of Odoo going forward.

This docker image only knows how to mount a single location for it's add-on modules. So out of the box it knows how to mount the Open Source distro of Odoo without any of the Enterprise modules installed.

To get around this I used the "enterprise" module location as authoritative:
    /Users/jimruga/code/enterprise-odoo/enterprise

When this docker starts it loads the default Open Source modules. After that it sees the Enterprise Odoo which replaces the Open Source modules in the memory map.
TODO: figure out how to just load the Enterprise Odoo directly and be able to use the /mnt/extra-addons for fictiv code

Because /mnt/extra-addons is being used to load the Enterprise code from my local disk I tried to symlink the "fictiv-odoo" modules inside the "enterprise" folder:
    fictiv_config -> /Users/jimruga/code/fictiv-odoo/fictiv_config/
    fictiv_customer -> /Users/jimruga/code/fictiv-odoo/fictiv_customer/
    fictiv_depgraph -> /Users/jimruga/code/fictiv-odoo/fictiv_depgraph/
    fictiv_digital_model -> /Users/jimruga/code/fictiv-odoo/fictiv_digital_model/
    fictiv_equipment -> /Users/jimruga/code/fictiv-odoo/fictiv_equipment/
    fictiv_holiday_calendar -> /Users/jimruga/code/fictiv-odoo/fictiv_holiday_calendar/
    fictiv_hotjar -> /Users/jimruga/code/fictiv-odoo/fictiv_hotjar/
    fictiv_import_event_wizard -> /Users/jimruga/code/fictiv-odoo/fictiv_import_event_wizard/
    fictiv_ir_attachment -> /Users/jimruga/code/fictiv-odoo/fictiv_ir_attachment/
    fictiv_program_management -> /Users/jimruga/code/fictiv-odoo/fictiv_program_management/
    fictiv_redis_session_store -> /Users/jimruga/code/fictiv-odoo/fictiv_redis_session_store/
    fictiv_vendor -> /Users/jimruga/code/fictiv-odoo/fictiv_vendor/
    fictiv_work_order -> /Users/jimruga/code/fictiv-odoo/fictiv_work_order/

This worked but subsequently causes load failures due to the Fictiv modules.
TODO: figure out why there's failures (necessary pre-requisite for upgrade testing)

The odoo.conf file has been updated to reflect Fictiv's development environment settings