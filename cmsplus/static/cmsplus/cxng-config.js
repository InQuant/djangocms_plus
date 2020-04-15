var CXNG_VERSION = '0.0.1';
var CXNG_TEMPL_Q = '?v=' + CXNG_VERSION;
var CXNG_STATIC_ROOT = '/static/cmsplus';

function cxngTemplateUrl(rel_path) {
    return CXNG_STATIC_ROOT + rel_path + CXNG_TEMPL_Q;
}
