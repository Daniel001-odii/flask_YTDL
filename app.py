from flask import Flask, render_template, request, send_file, make_response, jsonify
from pytube import YouTube
from urllib.parse import urlencode
from flask_cors import CORS

app = Flask(__name__)
CORS(app)



@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            try:
                yt = YouTube(url)
                video_streams = yt.streams.filter(file_extension="mp4", progressive=True)
                thumbnail_url = yt.thumbnail_url
                resolutions = [{"resolution": stream.resolution, "size_mb": stream.filesize / (1024 * 1024)} for stream in video_streams]
                return render_template("home.html", url=url, resolutions=resolutions, thumbnail_url=thumbnail_url)
            except Exception as e:
                error_message = "An error occurred: " + str(e)
                return render_template("home.html", error=error_message)
    return render_template("home.html")

@app.route("/download")
def download():
    url = request.args.get("url")
    resolution = request.args.get("resolution")
    
    if not url or not resolution:
        return "URL and resolution are required parameters."

    try:
        yt = YouTube(url)
        video_stream = yt.streams.filter(res=resolution, file_extension="mp4", progressive=True).first()
        video_file = video_stream.download()
        filename = f"{yt.title}_{resolution}.mp4"

        with open(video_file, 'rb') as file:
            video_content = file.read()
        
        response = make_response(video_content)
        response.headers['Content-Type'] = 'video/mp4'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    except Exception as e:
        return "An error occurred while downloading: " + str(e)


# API endpoint to fetch video information
@app.route("/api/video_info", methods=["GET"])
def api_video_info():
    url = request.args.get("url")
    if url:
        try:
            yt = YouTube(url)
            video_streams = yt.streams.filter(file_extension="mp4")
            audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()

            thumbnail_url = yt.thumbnail_url
            resolutions = [{"resolution": stream.resolution, "format": stream.mime_type, "size_mb": stream.filesize / (1024 * 1024), "download_link": f"/api/download?url={url}&resolution={stream.resolution}"} for stream in video_streams]
            
            if audio_stream:
                audio_format = audio_stream.mime_type.split("/")[-1]
                audio_link = f"/api/download?url={url}&resolution=audio"
                audio_size_mb = audio_stream.filesize / (1024 * 1024)
                audio_info = {"format": audio_format, "size_mb": audio_size_mb, "download_link": audio_link}
            else:
                audio_info = {"format": "N/A", "size_mb": 0, "download_link": ""}
            
            return jsonify({"title": yt.title, "resolutions": resolutions, "audio": audio_info, "thumbnail_url": thumbnail_url})
        except Exception as e:
            return jsonify({"error": "An error occurred: " + str(e)})
    return jsonify({"error": "URL parameter is required."})

    

@app.route("/api/download", methods=["GET"])
def api_download():
    url = request.args.get("url")
    resolution = request.args.get("resolution")
    
    if not url or not resolution:
        return jsonify({"error": "URL and resolution are required parameters."})

    try:
        yt = YouTube(url)
        if resolution == "audio":
            audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            audio_file = audio_stream.download()
            filename = f"{yt.title}_audio.{audio_stream.mime_type.split('/')[-1]}"

            with open(audio_file, 'rb') as file:
                audio_content = file.read()
            
            response = make_response(audio_content)
            response.headers['Content-Type'] = f'audio/{audio_stream.mime_type.split("/")[-1]}'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            return response
        else:
            video_stream = yt.streams.filter(res=resolution, file_extension="mp4").first()
            video_file = video_stream.download()
            filename = f"{yt.title}_{resolution}.mp4"

            with open(video_file, 'rb') as file:
                video_content = file.read()
            
            response = make_response(video_content)
            response.headers['Content-Type'] = 'video/mp4'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            return response

    except Exception as e:
        return jsonify({"error": "An error occurred while downloading: " + str(e)})


if __name__ == "__main__":
    app.run(debug=True)








# ... (previously defined routes for the web app)

