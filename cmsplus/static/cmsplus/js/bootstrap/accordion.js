var jsaccordion = {
    self: null,
    close_others: null,

    init : function (target) {
        // init() : initialize accordion
        // PARAM target : ID of accordion wrapper
        //       single : Only one drawer will only at a time
        self = document.querySelector(target);
        this.self = self;
        first_is_open = this.self.getAttribute('data-first-open');
        close_others = this.self.getAttribute('data-close-others');

        var headers = document.querySelectorAll(target + " .cmsplus-accordion-head");
        if (headers.length > 0) {
            // Single is false by default
            // Attach onclick event to headers
            for (var head of headers) { head.addEventListener("click", function () {
                jsaccordion.select(this, close_others);
            }); }
        }
        if (first_is_open) {
            var contents = this.self.getElementsByClassName("cmsplus-accordion-body");
            if (contents.length > 0) {
                contents[0].classList.add("open");
                contents[0].previousElementSibling.classList.add("open");
            }
        }
        this.openTabs();
    },

    openTabs: function () {
        var contents = this.self.parentElement.getElementsByClassName("cmsplus-accordion-body");
        if (contents.length > 0) {
            for (let c of contents) {
                if (!c.classList.contains('open')) {
                    c.style.maxHeight = null;
                } else {
                    c.style.maxHeight = c.scrollHeight + "px";
                }
            }
        }

    },

    toggleTab: function (element) {
        element.classList.toggle("open");
        element.previousElementSibling.classList.toggle("open")
    },

    select : function (event, close_others) {
        // Close all first
        if (close_others) {
            var contents = event.parentElement.getElementsByClassName("cmsplus-accordion-body");
            if (contents.length > 0) {
                for (var content of contents) {
                    if (content === event.nextElementSibling) {
                        continue;
                    }
                    content.classList.remove("open");
                    content.previousElementSibling.classList.remove("open");
                    content.style.maxHeight = null;
                }
            }
        }
        // Open selected drawer
        this.toggleTab(event.nextElementSibling);

        jsaccordion.openTabs();
    },

};