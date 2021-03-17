# hp27201a
Scott Baker, http://www.smbaker.com/

## Purpose

I reverse engineered the protocl of an HP 27201A speech output module that dates to the mid-1980s. This repo
contains a python module that implements the protocol and can control the SOM over serial.

## Pinout

```text
1 - G
2 - G
3 - NC?
4 - +5V
5 - SerIn 1B - Z8-P33, handshake line?
6 - SerIn 3B - Likely serial RX from inline dev, passthrough to Pin15
7 - SerIn 2B - Z8-P30, Serial RX (accepts escape sequences this pin)
8 - SerIn 4B
9 - G
10 - +12V
11 - -12V
12 - Serout U11-2
13 - Serout U11-1
14 - Serout U13-2 - serial TX (probably to inline dev)
15 - Serout U13-1 - serial TX (probably to host)
```

