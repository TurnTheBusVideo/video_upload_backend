import json
import math
import os

with open('/Users/annsarapaul/GitHub/TTB:video_upload_backend/Sample Video/translate_output.json') as f:
  data = json.load(f)

# Get specific frame
#ffmpeg -i "Vectors what even are they.mp4" -vf select='between(n\,160\,160)' -vsync 0 frames%d.png
#ffmpeg -ss 10 -i ../"Sample Video"/"Vectors what even are they.mp4" -vframes 1 output.png
#ffmpeg -i ../"Sample Video"/"Vectors what even are they.mp4" -ss 00:00:10 -t 00:00:10 -async 1 cut.mp4

start = 0.00
i = 1
for phrase in data:
    start = float(phrase['start_time'])
    end = float(phrase['end_time'])
    video_length = float(end) - float(start)
    audio_length = float(phrase['actual_time'])/1000
    video_filename = 'video_' + str(i).zfill(4) + ".mp4"
    f_video_filename = 'f_video_' + str(i).zfill(4) + ".mp4"
    audio_filename = 'audio_' + str(i).zfill(4) + ".mp3"
    raw_audio_file = 'speech_' + str(i).zfill(4) + ".mp3"
    end_in_sec = math.floor(float(end))
    start_in_sec = math.floor(start)
    audio_length_in_sec = math.ceil(float(phrase['actual_time'])/1000) + 2
    duration_in_sec = math.ceil(end - start)
    hour = math.floor(start_in_sec/3600)
    minute = math.floor((start_in_sec % 3600)/60)
    second = math.floor((start_in_sec % 3600) % 60)
    start_string = str(hour).zfill(2) + ':' + str(minute).zfill(2) + ':' + str(second).zfill(2)      
    hour = math.floor(duration_in_sec/3600)
    minute =  math.floor((duration_in_sec % 3600)/60)
    second = math.floor((duration_in_sec% 60))
    duration_string = str(hour).zfill(2) + ':' + str(minute).zfill(2) + ':' + str(second).zfill(2) 
    
    if audio_length > video_length:
        # need to extend video
        
        # get the frame at end time
              
        #Get the frame at the end of the video frame
        #ffmpeg -ss end_in_sec -i "Vectors whatdata even are they.mp4" -vframes 1 output.png
        #command = 'ffmpeg -ss ' + str(end_in_sec) + ' -i ../"Sample Video"/"Vectors what even are they.mp4" -vframes 1 output.png'
        #print('Running '+ command)
        #os.system(command)
        
        #Get the video snippit
        command = 'ffmpeg -i ../"Sample Video"/"Vectors what even are they.mp4" -ss '+ start_string +' -t '+ duration_string +' -async 1 ../"Sample Video"/' + video_filename
        print('Running '+ command)
        os.system(command)

        #Extend the video by adding the last frame to extend the video
        
        #ffmpeg -i ../"Sample Video"/"Vectors what even are they.mp4" -filter_complex "[0]showwaves=s=320x240:r=10[a-dur];[a-dur][0]overlay"-c:a copy -movflags +faststart output.mp4
        #ffmpeg -i "$file" -map 0 -af apad=whole_dur=7200 -c:v copy out.mp4
        command = 'ffmpeg -i ../"Sample Video"/'+video_filename+' -map 0 -af apad=whole_dur='+str(audio_length_in_sec)+' -c:v copy ../"Sample Video"/int_'+ video_filename
        print('Running '+ command)
        os.system(command)

        # Combine audio and video
        #ffmpeg -i ../"Sample Video"/"f_video_0005.mp4" -i ../"Sample Video"/speech_0005.mp3 -c:v copy -map 0:v:0 -map 1:a:0 out_video_0005.mp4
        command = 'ffmpeg -i ../"Sample Video"/int_'+ video_filename + ' -i ../"Sample Video"/' + raw_audio_file + ' -c:v copy -map 0:v:0 -map 1:a:0 ../"Sample Video"/' + f_video_filename
        print('Running '+ command)
        os.system(command)
    else:
        # need to extend audio

        #Get Video
        command = 'ffmpeg -i ../"Sample Video"/"Vectors what even are they.mp4" -ss '+ start_string +' -t '+ duration_string +' -async 1 ../"Sample Video"/' + video_filename
        print('Running '+ command)
        os.system(command)
        
        # Extend audio to match video by adding silence
        command = 'ffmpeg -i ../"Sample Video"/'+ video_filename + ' -i ../"Sample Video"/' + raw_audio_file + ' -c:v copy -af apad -shortest -map 0:v:0 -map 1:a:0 ../"Sample Video"/' + f_video_filename
        print('Running '+ command)
        os.system(command)

        # ffmpeg -i cut.mp4 -i speech_0001.mp3 -c:v copy -af apad -shortest -map 0:v:0 -map 1:a:0 output_1.mp4
    
    i = i +1 