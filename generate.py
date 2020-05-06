#!/usr/bin/env python3
import argparse
import os
import stat

os.chdir(os.path.dirname(__file__))

class Rule:

    def __init__(self, froms, tos, subjects, bodies, dest):
        self.froms = froms
        self.tos = tos
        self.subjects = subjects
        self.bodies = bodies
        self.dest = dest

    def __repr__(self):
        return '<Rule: f:{}, t:{} s:{} b:{} -> {}>'.format(self.froms, self.tos, self.subjects, self.bodies, self.dest)

    def generate(self):
        rules = []
        def add_subrule(subrules):
            rules.append('({})'.format(' || '.join(subrules)))
        if self.froms:
            add_subrule('/^From: {}/:h'.format(fro) for fro in self.froms)
        if self.tos:
            add_subrule('/^To: {}/:h'.format(to) for to in self.tos)
        if self.subjects:
            add_subrule('/^Subject: {}/:h'.format(subject) for subject in self.subjects)
        if self.subjects:
            add_subrule('/{}/:b'.format(body) for body in self.bodies)
        cond = ' && '.join(rules)
        return '{indent}if ( {cond} )\n{indent}{{\n{indent}  DEST="$MAILDIR/{dest}"\n{indent}  `test -d "$DEST" || maildirmake "$DEST"`\n{indent}  to "$DEST"\n{indent}}}\n'.format(cond=cond, dest=self.dest, indent='    ')

def read_config(config):
    froms = []
    tos = []
    subjects = []
    bodies = []
    rules = []
    for line_full in config.splitlines():
        line = line_full.strip()
        if line.startswith('#') or not line:
            continue
        elif line.startswith('f:'):
            froms.append(line[2:].strip())
        elif line.startswith('t:'):
            froms.append(line[2:].strip())
        elif line.startswith('s:'):
            subjects.append(line[2:].strip())
        elif line.startswith('b:'):
            bodies.append(line[2:].strip())
        elif line.startswith('->'):
            dest = line[2:].strip()
            if not froms and not tos and not subjects and not bodies:
                print('No rule before destination')
                return
            rules.append(Rule(froms, tos, subjects, bodies, dest))
            froms = []
            tos = []
            subjects = []
            bodies = []
        else:
            print('Unknown rule', line)
            return None
    if froms or tos or subjects or bodies:
        print('Config does not end with a destination')
        return None
    return rules

def generate(args):
    with open(args.config) as f:
        cfg = read_config(f.read())
    if not cfg:
        return
    with open(args.template) as f:
        template = f.read()
    template_parts = template.split('to "$MAILDIR"')
    if len(template_parts) > 2:
        print('Template changed, can not generate configuration.')
        return
    res = template_parts[0] + '\n'
    for rule in cfg:
        res += rule.generate() + '\n'
    res += '\n'
    res += '    to "$MAILDIR"'
    res += template_parts[1]
    with open(args.tempfile, 'w') as f:
        f.write(res)
    os.chmod(args.tempfile, stat.S_IREAD | stat.S_IWRITE)
    res = os.system('echo | EXT={} maildrop {}'.format(args.testuser, os.path.abspath(args.tempfile)))
    if res == 0:
        os.rename(args.tempfile, args.destination)

def main():
    parser = argparse.ArgumentParser(description="Generate a config file for maildrop.")
    parser.add_argument('--config', '-c', default='mailfilter.cfg')
    parser.add_argument('--destination', '-d', default='filter')
    parser.add_argument('--testuser', default='testuser')
    parser.add_argument('--tempfile', default='tempfilter')
    parser.add_argument('--template', '-t', default='/opt/uberspace/etc/spamfolder.template', help='Template to insert config into')
    args = parser.parse_args()
    generate(args)

if __name__ == '__main__':
    main()
