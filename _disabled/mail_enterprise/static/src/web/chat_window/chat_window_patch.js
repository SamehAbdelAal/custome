import { ChatWindow } from "@mail/core/common/chat_window";

import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";

// Note: useBackButton from @web_mobile/js/core/hooks is only available in Enterprise
// This patch provides basic functionality without mobile back button support

patch(ChatWindow.prototype, {
    setup() {
        super.setup();
        // Mobile back button handling removed - requires Enterprise web_mobile module
        // useBackButton(() => this.props.chatWindow.close());
        try {
            this.homeMenuService = useService("home_menu");
        } catch (e) {
            // home_menu service might not be available
            this.homeMenuService = null;
        }
    },
});
