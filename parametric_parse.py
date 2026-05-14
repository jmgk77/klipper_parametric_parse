# extras/parametric_parse.py

import re
import logging

class ParametricParse:
    def __init__(self, config):
        self.printer = config.get_printer()
        # 1. 'Consume' the inject key to satisfy the validator
        self.inject_data = config.get('inject', None)
        
        # 2. Get the raw ConfigParser directly from the config wrapper
        # In Klipper 0.13, this is the reliable way to get the parser during __init__
        self.raw_cfg = getattr(config, 'fileconfig', None)
        
        if self.raw_cfg:
            self.VAR_RE = re.compile(r'\(([^:)]+):([^)]+)\)')
            self._consume_user_variables(config)
            if self.inject_data:
                self._process_injections()
        else:
            logging.error("Parametric: Could not find fileconfig in config object.")

    def _consume_user_variables(self, config):
        RESERVED = {'inject'}  # add more if you add future keywords
        # consume all
        for option in self.raw_cfg.options('parametric_parse'):
            if option in RESERVED:
                continue
            # config.get() marks the key as consumed
            value = config.get(option)
            logging.info("Parametric: Registered variable [%s] = %s" % (option, value))         

    def _lookup(self, m):
        section, option = m.group(1).strip(), m.group(2).strip()
        if not self.raw_cfg.has_option(section, option):
            logging.error("Parametric: Reference (%s:%s) not found!" % (section, option))
            return "0"
        return str(self.raw_cfg.get(section, option, raw=True))

    def _process_injections(self):
        lines = [l.strip() for l in self.inject_data.split('\n') if l.strip() and not l.startswith('#')]

        for line in lines:
            try:
                # Remove comentários de final de linha antes de dar split
                line_content = line.split('#')[0].strip()
                if not line_content: 
                    continue

                # separa
                parts = [p.strip() for p in re.split(r'[.:]', line_content, 2)]
                if len(parts) < 3:
                    continue
                
                target_s, target_o, formula_str = parts[0], parts[1], parts[2]
                
                # Resolve (sec:opt) -> numeric strings
                resolved_str = self.VAR_RE.sub(self._lookup, formula_str)
                
                # Evaluate math
                eval_results = []
                for expr in resolved_str.split(','):
                    # Using a restricted eval
                    res = eval(expr.strip(), {"__builtins__": None}, {})
                    eval_results.append("%.3f" % float(res))
                
                final_val = ", ".join(eval_results)
                
                # Inject into the live ConfigParser memory
                if self.raw_cfg.has_section(target_s):
                    old = self.raw_cfg.get(target_s, target_o)
                    self.raw_cfg.set(target_s, target_o, final_val)
                    logging.info("Parametric: %s:%s updated to %s (was %s)" % (target_s, target_o, final_val, old))
                else:
                    logging.error("Parametric: Target section [%s] not found!" % target_s)
                    
            except Exception as e:
                logging.error("Parametric: Error on line [%s]: %s" % (line, str(e)))

def load_config(config):
    return ParametricParse(config)