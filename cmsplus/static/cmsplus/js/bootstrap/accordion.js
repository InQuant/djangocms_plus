const jsaccordion = {
    init : function (target) {
        // init() : initialize accordion
        // PARAM target : ID of accordion wrapper
        //       single : Only one drawer will only at a time
        const self = this
        const accordion = document.querySelector(target);

        let first_is_open = accordion.getAttribute('data-first-open') !== "false";
        let close_others = accordion.getAttribute('data-close-others') !== "false";

        var headers = accordion.querySelectorAll(".cmsplus-accordion-head");

        if (headers.length > 0) {
            // Single is false by default
            // Attach onclick event to headers
            for (let head of headers) {
                head.addEventListener("click", function () {
                    jsaccordion.select(accordion, head, close_others);
                });
            }
        }
        if (first_is_open) {
            var contents = accordion.getElementsByClassName("cmsplus-accordion-body");
            if (contents.length > 0) {
                this.toggleTab(contents[0])
            }
        }
        this.openTabs(accordion);
    },

    openTabs: function (accordion) {
        var contents = accordion.parentElement.getElementsByClassName("cmsplus-accordion-body");
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
    closeTab: function (element)  {
        element.classList.remove("open");
        element.previousElementSibling.classList.remove("open")
    },
    select : function (accordion, target, close_others) {
        // Close all first
        if (close_others) {
            // get all body elements in accordion
            const contents = accordion.getElementsByClassName("cmsplus-accordion-body");
            for (let content of contents) {
                this.closeTab(content)
            }
        }
        // Open selected drawer
        this.toggleTab(target.nextElementSibling);

        jsaccordion.openTabs(accordion);
    },

};