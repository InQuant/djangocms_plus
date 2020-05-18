// angular module
var cmsplusOsm = angular.module('cmsplus.osm', ['ui-leaflet']);

/*
 * cng component cxng-openstreet-map
 *
 */
function cxngOpenstreetMapCtrl($scope, $element, $attrs, leafletData) {
    console.log('cxngOpenstreetMapCtrl');
    var ctrl = this;

    ctrl.$onInit = function () {
        console.log(MAP_CONFIGS[ctrl.instanceId]);
        ctrl.config = MAP_CONFIGS[ctrl.instanceId];

        angular.extend($scope, ctrl.config);

        /*
        leafletData.getMap().then(function(map) {
            var StamenToner = L.tileLayer(
                'https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}.{ext}',
                {
                    attribution: '<a href="http://stamen.com">Stamen</a>',
                    //minZoom: 0,
                    //maxZoom: 20,
                    ext: 'png'
                });
            map.addLayer(StamenToner);
        }); */

        leafletData.getMap().then(function(map) {

            if (ctrl.config.layer == 'stamen') {
                var StamenToner = L.tileLayer(
                    'https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}.{ext}',
                    {
                        attribution: '<a href="http://stamen.com">Stamen</a>',
                        //minZoom: 0,
                        //maxZoom: 20,
                        ext: 'png'
                    });
                map.addLayer(StamenToner);
            } else if (ctrl.config.layer) {
                var gl = L.mapboxGL({
                    attribution: '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OSM contributors</a>',
                    accessToken: 'not-needed',
                    style: '/static/cmsplus/osm/black.json'
                });
                map.addLayer(gl);
            }

            // add markers
            for (var i=0; i < $scope.markers.length; i++) {
                var m = $scope.markers[i];

                var divIcon = L.divIcon({
                    className: 'c-osm-marker c-osm-custom-marker c-osm-marker-' + m.name,
                });
                let opt = {
                    icon: divIcon,
                };

                opt.marker_id = m.name;
                let marker = L.marker([m.lat, m.lon], opt).addTo(map);
            }
        });
    };

}
cmsplusOsm.component('cxngOpenstreetMap', {
    bindings: {
        instanceId: '@',
    },
    templateUrl: cxngTemplateUrl('/osm/osm.html'),
    controller: cxngOpenstreetMapCtrl,
})
