#!/bin/bash
# flux: --job-name={{job_name}}
# flux: --env=CORES={{cores}}
# flux: --output=time.out
# flux: --error=error.out
# flux: --nslots={{cores}}
{%- if run_time_max %}
# flux: --time-limit={{run_time_max}}s
{%- endif %}
{%- if dependency_list %}
{%- for jobid in dependency_list %}
# flux: --dependency=afterok:{{jobid}}
{%- endfor %}
{%- endif %}

{{command}}