
#
日期：2026/06/04


# 类名
RawvConverter

# 音视频概念
1.视频处理：
        转码
        封装（remux）:换个盒子装起来（MP4）
        PTS = presentation time stamp（播放时间），控制音画同步用的
        推流
2.音频处理：
    Ⅰ.A-Law：压缩后的语音格式
    Ⅱ.PCM:原始声音
    Ⅲ.
    Ⅳ.



# 代码
1.读取rawv文件流的头部header,解析header（分辨率/编码/音频参数）。拿到以下数据
            version	rawv版本
            codec	视频编码类型
            width	分辨率
            height	分辨率
            audioRate	采样率
            channels	声道
```java
   val version = wrap.getShort().toInt() and 0xFFFF
            val flags = wrap.getShort().toInt() and 0xFFFF
            val vCodec = wrap.get()
            val aCodec = wrap.get()
            val width = wrap.getShort().toInt() and 0xFFFF
            val height = wrap.getShort().toInt() and 0xFFFF
            val audioRate = wrap.getInt()
            val audioCh = wrap.get().toInt() and 0xFF
        
```

因为这个文件流读取

2.逐帧读取除了header剩下的32位字节（video/audio packet）
```java
 // 3. 循环解析帧
            val frameHeader = ByteArray(14)
            var firstPts: Long = -1
            var lastVideoPtsUs: Long = -1
            var totalAudioSamples = 0L
            var hasReachedKeyFrame = false
            
            while (inputStream.available() >= 14) {
                if (inputStream.read(frameHeader) != 14) break
                
                val fWrap = ByteBuffer.wrap(frameHeader).order(ByteOrder.BIG_ENDIAN)
                val type = fWrap.get().toInt() and 0xFF
                val fFlags = fWrap.get().toInt() and 0xFF
                var ptsOff = fWrap.getInt().toLong() and 0xFFFFFFFFL
                if (ptsOff > 0xFFFFFFF) ptsOff = Integer.reverseBytes(ptsOff.toInt()).toLong() and 0xFFFFFFFFL

                fWrap.getShort() // skip dtOff
                var length = fWrap.getInt()
                if (length < 0 || length > 1024 * 1024) length = Integer.reverseBytes(length)
                
                val seq = fWrap.getShort().toInt() and 0xFFFF
                if (length <= 0 || length > 10 * 1024 * 1024) continue
                
                val payload = ByteArray(length)
                if (inputStream.read(payload) != length) break
                
                // 必须等到第一个视频关键帧才开始写入，否则 MP4 无法播放或封装报错
                if (!hasReachedKeyFrame) {
                    if (type == 1 && (fFlags and 0x01 != 0)) {
                        hasReachedKeyFrame = true
                        firstPts = ptsOff
                    } else continue
                }
```

3.PTS控制视频帧和音频同步
```java
 if (type == 1) { // 视频帧
                    // 保护：确保 PTS 严格递增
                    var finalPts = relativePtsUs
                    if (finalPts <= lastVideoPtsUs) finalPts = lastVideoPtsUs + 1000
                    lastVideoPtsUs = finalPts

                    val bp = BytePointer(length.toLong())
                    bp.put(payload, 0, length)
                    
                    videoPkt.data(bp)
                    videoPkt.size(length)
                    videoPkt.stream_index(0)
                    videoPkt.pts(finalPts)
                    videoPkt.dts(finalPts)
                    
                    if (fFlags and 0x01 != 0) videoPkt.flags(avcodec.AV_PKT_FLAG_KEY)
                    else videoPkt.flags(0)

                    recorder.recordPacket(videoPkt)
                    videoPkt.data(null)
                    bp.close()
                } else if (type == 2) { // 音频帧
                    val pcmData = ShortArray(length)
                    for (i in 0 until length) {
                        pcmData[i] = alawToLinear(payload[i])
                    }
                    
                    val audioPts = totalAudioSamples * 1000000L / (if (realAudioRate > 0) realAudioRate else 16000)
                    // 同步保护：音频时间戳不能领先视频太多
                    if (audioPts <= lastVideoPtsUs + 2000000L) {
                        recorder.timestamp = audioPts
                        recorder.recordSamples(ShortBuffer.wrap(pcmData))
                        totalAudioSamples += length
                    }
                }
                
                onProgress((fileLength - inputStream.available()).toFloat() / fileLength)
            }
            
```