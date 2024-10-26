# uberspace-mailfilter
Mailfilter for Uberspace

Generates a sieve script based on a custom config.

Write a config file `mailfilter.cfg`, then call `./generate.py` to generate and install the sieve script.

The config file consists of several rule groups. Each rule group consists of one rule per line, followed by a destination. For rules of the same type, only one of them has to hold, for different types all have to hold. For the rules, regex are allowed. Comments with `#` are allowed at the line start.

- `f:`: From header
- `t:`: To header
- `s:`: Subject
- `b:`: Body
- `->`: Destination

Example config:

```
t: my-app@example.com
-> .INBOX.App
f: a@example.com
f: b@example.com
s: .*Spam.*
b: This is spam
-> .Spam
```
