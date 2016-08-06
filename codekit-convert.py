#!/usr/bin/python

import sys
import json
import os

fileTypes = {
    "php"  : 8192,
    "js"   : 64,
    "css"  : 16,
    "less" : 1,
    "png"  : 32768,
    "jpg"  : 16384,

}

def genJsSection(source, minimise=False, genSourceMap=False):
    sourceDir = os.path.dirname(source)

    section = "gulp.src('" + source + "')\n"\
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
    section = section + ".pipe(rename({suffix: '-" + suffix + "''}))\n"\
    ".pipe(gulp.dest('./" + sourceDir + "'));"
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
    
    gulp.src(__filename)
        .pipe(open(\{uri: '**** SERVER URI ****'\}));
});

gulp.task('default', ['watch', 'less']);
"""

def main():
    if len(sys.argv) < 2:
        print "You need to pass a codekit config file as the second argument"
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
    print len(codekitData['files'])


if __name__ == "__main__":
    main()