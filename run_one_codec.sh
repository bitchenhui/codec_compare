#!/bin/bash
# author:ppchduan
# date:20220910
# intro:prepare to codectest in mac
# rely：yasm,nasm


runMain(){   
    local codec_name=$1
    local codec_level=$2
    local currentDir=`pwd`
    #下载静态版本ffmpeg
    source="ffmpeg"
    version="-5.1.1"
    if [ ! -r $source ]
    then
        echo "no ffmpeg, we need to download."
        #macos ffmpeg地址
        curl https://evermeet.cx/pub/ffmpeg/${source}${version}.zip | tar xj || exit 1
        #configure_flags="--cc=/usr/bin/clang --prefix=/opt/ffmpeg --extra-version=tessus --enable-avisynth --enable-fontconfig --enable-gpl 
        #--enable-libaom --enable-libass --enable-libbluray --enable-libdav1d --enable-libfreetype --enable-libgsm --enable-libmodplug 
        #--enable-libmp3lame --enable-libmysofa --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libopenh264 --enable-libopenjpeg 
        #--enable-libopus --enable-librubberband --enable-libshine --enable-libsnappy --enable-libsoxr --enable-libspeex --enable-libtheora 
        #--enable-libtwolame --enable-libvidstab --enable-libvmaf --enable-libvo-amrwbenc --enable-libvorbis --enable-libvpx --enable-libwebp --enable-libx265 
        #--enable-libxavs --enable-libxvid --enable-libzimg --enable-libzmq --enable-libzvbi --enable-version3 --pkg-config-flags=--static --disable-ffplay"

    fi
    #获得ffmpeg权限
    chmod +x ${currentDir}/ffmpeg

    python3 -u ${currentDir}/src/main.py -m ${codec_level} -c ${codec_name}
}
Codec1=$1
Level1=$2
runMain    "${Codec1}" "${Level1}"