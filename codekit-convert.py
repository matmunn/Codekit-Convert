#!/usr/bin/python

import sys
import json
import os

debug = True

fileTypes = {
    "php"  : 8192,
    "js"   : 64,
    "css"  : 16,
    "less" : 1,
    "png"  : 32768,
    "jpg"  : 16384,

}

def genJsSection(source, destName, minimise=False, genSourceMap=False):
    dests = os.path.split(destName)

    section = "gulp.src('." + source + "')\n"\
    ".pipe(include())\n"\
    "    .on('error', console.log)\n"
    if minimise:
        if genSourceMap:
            section = section + ".pipe(sourcemaps.init())\n"
        section = section + ".pipe(uglify())\n"
        if genSourceMap:
            section = section + ".pipe(sourcemaps.write('./maps'))\n"
        suffix = "min"
    else:
        suffix = "dist"
    section = section + ".pipe(rename({basename: '" + dests[1] + "'}))\n"\
    ".pipe(gulp.dest('." + dests[0] + "'));\n\n"
    return section

gulpBase = """
var gulp = require('gulp'),
    less = require('gulp-less'),
    autoprefixer = require('gulp-autoprefixer'),
    cssnano = require('gulp-cssnano'),
    jshint = require('gulp-jshint'),
    uglify = require('gulp-uglify'),
    include = require('gulp-codekit'),
    notify = require('gulp-notify'),
    watch = require('gulp-watch'),
    livereload = require('gulp-livereload'),
    del = require('del'),
    rename = require('gulp-rename'),
    sourcemaps = require('gulp-sourcemaps'),
    open = require('gulp-open');

gulp.task('js', function() {
    **** JS SECTIONS ****
});

gulp.task('less', function() {
    gulp.src('./css/custom.less')
        .pipe(sourcemaps.init())
        .pipe(less())
        .pipe(cssnano())
        .pipe(sourcemaps.write('./maps'))
        .pipe(rename('custom-min.css'))
        .pipe(gulp.dest('./css'));
    gulp.src('./css/interactive-map.less')
        .pipe(sourcemaps.init())
        .pipe(less())
        .pipe(cssnano())
        .pipe(sourcemaps.write('./maps'))
        .pipe(rename('interactive-map-min.css'))
        .pipe(gulp.dest('./css'))
        .pipe(notify({message: 'LESS files compiled', onLast: true}))
        .pipe(livereload());
});

gulp.task('php', function() {
    gulp.src('hey').pipe(livereload());
})

gulp.task('watch', function() {
    livereload.listen();
    gulp.watch('css/*.less', ['less']);
    gulp.watch(['js/main.js', 'js/interactive-map/interactive-map.js'], ['js']);
    gulp.watch('**/*.php', ['php']);
    
    **** SERVER URI ****
});

gulp.task('default', ['watch', 'less', 'js']);
"""

def main():
    global gulpBase
    javascriptSections = ''

    if len(sys.argv) < 2:
        print "You need to pass a Codekit config file as the second argument"
        sys.exit(1)

    codekitFile = sys.argv[1]
    try:
        with open(codekitFile, "r") as fp:
            codekitData = json.load(fp)
    except IOError:
        print "Couldn't read the specified source file"
        sys.exit(1)

    # print json.dumps(codekitData['files'])
    # print genJsSection('js/test.js', False, True)
    # print len(codekitData['files'])
    # print genJsSection('js/test.js')

    for file in codekitData['files']:
        data = codekitData['files'][file]
        if data['fileType'] == fileTypes['js']:
            if data['ignore'] == 0:
                # print "we need an output"
                javascriptSections = javascriptSections + genJsSection(file, data['outputAbbreviatedPath'], True)

    gulpBase = gulpBase.replace("**** JS SECTIONS ****", javascriptSections)

    if codekitData['projectSettings']['alwaysUseExternalServer'] is 1:
        serverString = "gulp.src(__filename)\n"\
        "        .pipe(open({uri: '" + codekitData['projectSettings']['externalServerAddress'] + "'}));"

        gulpBase = gulpBase.replace("**** SERVER URI ****", serverString)

    if debug:
        print gulpBase
    # else:
    #     try:
    #         with open('gulpfile.js', 'w') as fp:
    #             fp.write(gulpBase)
    #     except IOError:
    #         print "Couldn't write gulpfile.js"
    #         sys.exit(1)

if __name__ == "__main__":
    main()