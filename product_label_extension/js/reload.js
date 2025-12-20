/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
    async onFieldChanged(event) {
        await super.onFieldChanged(event);
        if (event.detail.name === "attribute_line_ids") {
            if (!this.model.root.isNew) {
                await this.model.root.save();
                await this.actionService.doAction({
                    type: "ir.actions.client",
                    tag: "reload",
                });
            }
        }
    },
});
