#!/usr/bin/env python3
import argparse
import os
import stat

os.chdir(os.path.dirname(__file__))

class Rule:

    def __init__(self, froms, tos, subjects, bodies, dest, forward):
        self.froms = froms
        self.tos = tos
        self.subjects = subjects
        self.bodies = bodies
        self.dest = dest
        self.forward = forward

    def __repr__(self):
        return '<Rule: f:{}, t:{} s:{} b:{} -> {} ---> {}>'.format(self.froms, self.tos, self.subjects, self.bodies, self.dest, self.forward)

    def generate(self):
        if self.forward:
            action = 'redirect "{}";'.format(self.forward)
        else:
            action = 'fileinto "{}";'.format(self.dest)
        rules = []
        def add_subrule(subrules):
            subs = list(subrules)
            if len(subs) == 1:
                rules.append(subs[0])
            else:
                rules.append('anyof({})'.format(', '.join(subs)))
        if self.froms:
            add_subrule('address :regex "from" "{}"'.format(fro) for fro in self.froms)
        if self.tos:
            add_subrule('address :regex "to" "{}"'.format(to) for to in self.tos)
        if self.subjects:
            add_subrule('header :regex "subject" "{}"'.format(subject) for subject in self.subjects)
        if self.bodies:
            add_subrule('body :regex "{}"'.format(body) for body in self.bodies)
        if not rules:
            return action
        if len(rules) == 1:
            return 'if {} {{\n  {}\n  stop;\n}}'.format(rules[0], action)
        return 'if allof({}) {{\n  {}\n  stop;\n}}'.format(', '.join(rules), action)

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
            tos.append(line[2:].strip())
        elif line.startswith('s:'):
            subjects.append(line[2:].strip())
        elif line.startswith('b:'):
            bodies.append(line[2:].strip())
        elif line.startswith('--->'):
            dest = line[4:].strip()
            rules.append(Rule(froms, tos, subjects, bodies, None, dest))
            froms = []
            tos = []
            subjects = []
            bodies = []
        elif line.startswith('->'):
            dest = line[2:].strip()
            rules.append(Rule(froms, tos, subjects, bodies, dest, None))
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
    
    destination = os.path.expanduser(args.destination)
    
    with open(destination, 'w') as f:
        print('require ["fileinto", "regex"];', file=f)
        for rule in cfg:
            print(rule.generate(), file=f)
    os.system('sievec {}'.format(destination))

def main():
    parser = argparse.ArgumentParser(description="Generate a config file for sieve.")
    parser.add_argument('--config', '-c', default='mailfilter.cfg')
    parser.add_argument('--destination', '-d', default='~/users/catchall/sieve/filter.sieve')
    args = parser.parse_args()
    generate(args)

if __name__ == '__main__':
    main()
