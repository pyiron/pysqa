#!/bin/bash
# flux: --job-name={{job_name}}
# flux: --env=CORES={{cores}}
# flux: --output=time.out
# flux: --error=error.out
# flux: -n {{cores}}
{%- if run_time_max %}
# flux: -t {{ [1, run_time_max // 60]|max }}
{%- endif %}
{%- if dependency %}
{%- for jobid in dependency %}
# flux: --dependency=afterok:{{jobid}}
{%- endfor %}
{%- endif %}

{{command}}