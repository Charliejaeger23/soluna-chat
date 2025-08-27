
[app]
title = Soluna Chat
package.name = solunachat
package.domain = org.example
source.dir = .
source.include_exts = py,kv,txt,md
version = 0.1
requirements = python3,kivy,requests,websockets,pyjwt,plyer
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2

[android]
android.permissions = INTERNET,VIBRATE
