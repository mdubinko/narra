# Requires GNU Make 4+
need := 4.0

.RECIPEPREFIX := >


WORK_DIR := /mdubinko/Downloads/narrative/scratch


QUIET     = @

SHELL     = bash
AWK      := awk
CP       := cp
RM       := rm -f
LS       := ls -l
SOX      := sox

.PHONY: all

%.wav : %.mp3
> $(SOX) $< $@

