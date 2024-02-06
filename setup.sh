#!/bin/bash

cp -r sample_images images &&
cp .env.example .env &&
cp alembic.ini.example alembic.ini &&
mkdir db &&
mkdir log
