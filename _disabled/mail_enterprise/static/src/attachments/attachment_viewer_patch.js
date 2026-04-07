import { FileViewer } from "@web/core/file_viewer/file_viewer";
import { patch } from "@web/core/utils/patch";

// Note: useBackButton from @web_mobile/js/core/hooks is only available in Enterprise
// This patch provides basic functionality without mobile back button support

patch(FileViewer.prototype, {
    setup() {
        super.setup();
        // Mobile back button handling removed - requires Enterprise web_mobile module
    },
});
