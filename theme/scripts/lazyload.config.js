// lazyload config
var MODULE_CONFIG = {
    notie:           [
                    '/static/libs/list.js/dist/list.js',
                    '/static/libs/notie/dist/notie.min.js',
                    '/static/scripts/plugins/notie.js',
                    ],
    chat:           [
                      '/static/libs/list.js/dist/list.js',
                      '/static/libs/notie/dist/notie.min.js',
                      '/static/scripts/plugins/notie.js',
                      '/static/scripts/app/chat.js'
                    ],
    mail:           [
                      '/static/libs/list.js/dist/list.js',
                      '/static/libs/notie/dist/notie.min.js',
                      '/static/scripts/plugins/notie.js',
                      '/static/scripts/app/mail.js'
                    ],
    user:           [
                      '/static/libs/list.js/dist/list.js',
                      '/static/libs/notie/dist/notie.min.js',
                      '/static/scripts/plugins/notie.js',
                      '/static/scripts/app/user.js'
                    ],
    screenfull:     [
                      '/static/libs/screenfull/dist/screenfull.js',
                      '/static/scripts/plugins/screenfull.js'
                    ],
    jscroll:        [
                      '/static/libs/jscroll/jquery.jscroll.min.js'
                    ],
    stick_in_parent:[
                      '/static/libs/sticky-kit/jquery.sticky-kit.min.js'
                    ],
    scrollreveal:   [
                      '/static/libs/scrollreveal/dist/scrollreveal.min.js',
                      '/static/scripts/plugins/jquery.scrollreveal.js'
                    ],
    owlCarousel:    [
                      '/static/libs/owl.carousel/dist/assets/owl.carousel.min.css',
                      '/static/libs/owl.carousel/dist/assets/owl.theme.css',
                      '/static/libs/owl.carousel/dist/owl.carousel.min.js'
                    ],
    html5sortable:  [
                      '/static/libs/html5sortable/dist/html.sortable.min.js',
                      '/static/scripts/plugins/jquery.html5sortable.js',
                      '/static/scripts/plugins/sortable.js'
                    ],
    easyPieChart:   [
                      '/static/libs/easy-pie-chart/dist/jquery.easypiechart.min.js'
                    ],
    peity:          [
                      '/static/libs/peity/jquery.peity.js',
                      '/static/scripts/plugins/jquery.peity.tooltip.js',
                    ],
    chart:          [
                      '/static/libs/moment/min/moment-with-locales.min.js',
                      '/static/libs/chart.js/dist/Chart.min.js',
                      '/static/scripts/plugins/jquery.chart.js',
                      '/static/scripts/plugins/chartjs.js'
                    ],
    dataTable:      [
                      '/static/libs/datatables/media/js/jquery.dataTables.min.js',
                      '/static/libs/datatables.net-bs4/js/dataTables.bootstrap4.js',
                      '/static/libs/datatables.net-bs4/css/dataTables.bootstrap4.css',
                      '/static/scripts/plugins/datatable.js'
                    ],
    bootstrapTable: [
                      '/static/libs/bootstrap-table/dist/bootstrap-table.min.css',
                      '/static/libs/bootstrap-table/dist/bootstrap-table.min.js',
                      '/static/libs/bootstrap-table/dist/extensions/export/bootstrap-table-export.min.js',
                      '/static/libs/bootstrap-table/dist/extensions/mobile/bootstrap-table-mobile.min.js',
                      '/static/scripts/plugins/tableExport.min.js',
                      '/static/scripts/plugins/bootstrap-table.js'
                    ],
    bootstrapWizard:[
                      '/static/libs/twitter-bootstrap-wizard/jquery.bootstrap.wizard.min.js'
                    ],
    dropzone:       [
                      '/static/libs/dropzone/dist/min/dropzone.min.js',
                      '/static/libs/dropzone/dist/min/dropzone.min.css'
                    ],
    datetimepicker: [
                      '/static/libs/tempusdominus-bootstrap-4/build/css/tempusdominus-bootstrap-4.min.css',
                      '/static/libs/moment/min/moment-with-locales.min.js',
                      '/static/libs/tempusdominus-bootstrap-4/build/js/tempusdominus-bootstrap-4.min.js',
                      '/static/scripts/plugins/datetimepicker.js'
                    ],
    datepicker:     [
                      "/static/libs/bootstrap-datepicker/dist/js/bootstrap-datepicker.min.js",
                      "/static/libs/bootstrap-datepicker/dist/css/bootstrap-datepicker.min.css",
                    ],
    fullCalendar:   [
                      '/static/libs/moment/min/moment-with-locales.min.js',
                      '/static/libs/fullcalendar/dist/fullcalendar.min.js',
                      '/static/libs/fullcalendar/dist/fullcalendar.min.css',
                      '/static/scripts/plugins/fullcalendar.js'
                    ],
    parsley:        [
                      '/static/libs/parsleyjs/dist/parsley.min.js'
                    ],
    select2:        [
                      '/static/libs/select2/dist/css/select2.min.css',
                      '/static/libs/select2/dist/js/select2.min.js',
                      '/static/scripts/plugins/select2.js'
                    ],
    summernote:     [
                      '/static/libs/summernote/dist/summernote.css',
                      '/static/libs/summernote/dist/summernote-bs4.css',
                      '/static/libs/summernote/dist/summernote.min.js',
                      '/static/libs/summernote/dist/summernote-bs4.min.js'
                    ],
    vectorMap:      [
                      '/static/libs/jqvmap/dist/jqvmap.min.css',
                      '/static/libs/jqvmap/dist/jquery.vmap.js',
                      '/static/libs/jqvmap/dist/maps/jquery.vmap.world.js',
                      '/static/libs/jqvmap/dist/maps/jquery.vmap.usa.js',
                      '/static/libs/jqvmap/dist/maps/jquery.vmap.france.js',
                      '/static/scripts/plugins/jqvmap.js'
                    ],
    waves:          [
                      '/static/libs/node-waves/dist/waves.min.css',
                      '/static/libs/node-waves/dist/waves.min.js',
                      '/static/scripts/plugins/waves.js'
                    ]
  };

var MODULE_OPTION_CONFIG = {
  parsley: {
    errorClass: 'is-invalid',
    successClass: 'is-valid',
    errorsWrapper: '<ul class="list-unstyled text-sm mt-1 text-muted"></ul>'
  }
}
