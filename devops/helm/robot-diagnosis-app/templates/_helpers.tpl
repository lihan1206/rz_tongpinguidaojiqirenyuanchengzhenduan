{{/*
Expand the name of the chart.
*/}}
{{- define "robot-diagnosis.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "robot-diagnosis.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "robot-diagnosis.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "robot-diagnosis.labels" -}}
helm.sh/chart: {{ include "robot-diagnosis.chart" . }}
{{ include "robot-diagnosis.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: robot-diagnosis-system
environment: {{ .Values.global.environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "robot-diagnosis.selectorLabels" -}}
app.kubernetes.io/name: {{ include "robot-diagnosis.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "robot-diagnosis.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "robot-diagnosis.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Backend labels
*/}}
{{- define "robot-diagnosis.backend.labels" -}}
{{ include "robot-diagnosis.labels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "robot-diagnosis.backend.selectorLabels" -}}
{{ include "robot-diagnosis.selectorLabels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "robot-diagnosis.frontend.labels" -}}
{{ include "robot-diagnosis.labels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "robot-diagnosis.frontend.selectorLabels" -}}
{{ include "robot-diagnosis.selectorLabels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Java Service labels
*/}}
{{- define "robot-diagnosis.java.labels" -}}
{{ include "robot-diagnosis.labels" . }}
app.kubernetes.io/component: java-service
{{- end }}

{{/*
Java Service selector labels
*/}}
{{- define "robot-diagnosis.java.selectorLabels" -}}
{{ include "robot-diagnosis.selectorLabels" . }}
app.kubernetes.io/component: java-service
{{- end }}

{{/*
Ingress annotations
*/}}
{{- define "robot-diagnosis.ingress.annotations" -}}
{{- if .Values.ingress.annotations }}
{{- toYaml .Values.ingress.annotations }}
{{- end }}
{{- if .Values.canary.enabled }}
flagger.app/primary-hpa: "{{ include "robot-diagnosis.fullname" . }}"
flagger.app/canary-weight: "{{ .Values.canary.weight }}"
{{- end }}
{{- end }}

{{/*
Generate environment variables from config map
*/}}
{{- define "robot-diagnosis.envFromConfigMap" -}}
{{- range $key, $value := . }}
- name: {{ $key }}
  valueFrom:
    configMapKeyRef:
      name: {{ include "robot-diagnosis.fullname" $ }}
      key: {{ $key }}
{{- end }}
{{- end }}

{{/*
Generate environment variables from secret
*/}}
{{- define "robot-diagnosis.envFromSecret" -}}
{{- range . }}
- name: {{ .name }}
  valueFrom:
    secretKeyRef:
      name: {{ .secretName }}
      key: {{ .key }}
{{- end }}
{{- end }}

{{/*
Pod security context
*/}}
{{- define "robot-diagnosis.podSecurityContext" -}}
{{- if .Values.podSecurityContext }}
securityContext:
  {{- toYaml .Values.podSecurityContext | nindent 2 }}
{{- end }}
{{- end }}

{{/*
Container security context
*/}}
{{- define "robot-diagnosis.securityContext" -}}
{{- if .Values.securityContext }}
securityContext:
  {{- toYaml .Values.securityContext | nindent 2 }}
{{- end }}
{{- end }}

{{/*
Resource constraints
*/}}
{{- define "robot-diagnosis.resources" -}}
{{- if .resources }}
resources:
  {{- toYaml .resources | nindent 2 }}
{{- end }}
{{- end }}

{{/*
Probe configuration
*/}}
{{- define "robot-diagnosis.probes" -}}
{{- if .livenessProbe.enabled }}
livenessProbe:
  httpGet:
    path: {{ .livenessProbe.path }}
    port: {{ .livenessProbe.port }}
  initialDelaySeconds: {{ .livenessProbe.initialDelaySeconds }}
  periodSeconds: {{ .livenessProbe.periodSeconds }}
  timeoutSeconds: {{ .livenessProbe.timeoutSeconds }}
  failureThreshold: {{ .livenessProbe.failureThreshold }}
{{- end }}
{{- if .readinessProbe.enabled }}
readinessProbe:
  httpGet:
    path: {{ .readinessProbe.path }}
    port: {{ .readinessProbe.port }}
  initialDelaySeconds: {{ .readinessProbe.initialDelaySeconds }}
  periodSeconds: {{ .readinessProbe.periodSeconds }}
  timeoutSeconds: {{ .readinessProbe.timeoutSeconds }}
  failureThreshold: {{ .readinessProbe.failureThreshold }}
{{- end }}
{{- end }}
