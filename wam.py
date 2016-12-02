#!/usr/bin/env python

from urllib.request import urlretrieve
from zipfile import ZipFile

import click
from bs4 import BeautifulSoup
from retrying import retry
from selenium import webdriver

## known_addons = ('tradeskill-master',
##                 'battlegroundtargets',
##                 'autoturnin',
##                 'daily-global-check',
##                 'daily-global-check_professions',
##                 'daily-global-check_garrisonmissi',
##                 'daily-global-check_workorders',
##                 'healers-have-to-die',
##                 'junkit',
##                 'lootappraiser',
##                 'master-plan',
##                 'quartz',
##                 'recount',
##                 'shadowed-unit-frames',
##                 'tellmewhen',
##                 'tidy-plates',
##                 'tradeskill-master',
##                 'tradeskillmaster_accounting',
##                 'tradeskillmaster_apphelper',
##                 'tradeskillmaster_auctiondb',
##                 'tradeskillmaster_auctioning',
##                 'tradeskillmaster_crafting',
##                 'tradeskillmaster_destroying',
##                 'tradeskillmaster_mailing',
##                 'tradeskillmaster_shopping',
##                 'tradeskillmaster_vendoring',
##                 'tradeskillmaster_warehousing',
##                 'world-quest-tracker',
##                 'deadly-boss-mods',
##                 'dbm-pvp',
##                 'gladius',
##                 'omnibar',
##                 'trufigcd',
##                 'bandaid',
##                 'simulationcraft',
##                 'pawn',
##                 'quest_completist',
##                 'telemancy',
##                 'decursive',
##                 'weakauras-2',
##                 'enemy-grid',
##                 'askmrrobot',
## #                'conslegion',
##                 )

with open('addons.txt') as f:
    known_addons = set(f.read().splitlines())

main_link = 'http://mods.curse.com/addons/wow/'


def click_download_button(driver):
    source = BeautifulSoup(driver.page_source, 'html.parser')
    links = source.findAll('a', href=True, text='Download Now')
    for link in links:
        href = link['href']
        download_link = driver.find_element_by_xpath('//a[@href="'+href+'"]')
        download_link.click()


def download_file(driver):
    source = BeautifulSoup(driver.page_source, 'html.parser')
    links = source.findAll('a', href=True, text='click here')
    file_name = None
    for link in links:
        download_link = link['data-href']
        file_name = download_link.split('/')[-1]
        urlretrieve(download_link, file_name)
    return file_name


class AddOn:
    def __init__(self, name):
        self.name = name

    def load(self):
        driver = webdriver.PhantomJS()
        driver.set_window_size(1120, 550)
        driver.get(main_link + self.name)
        self.driver = driver

    def fetch(self):
        click_download_button(self.driver)
        self.filename = download_file(self.driver)

    def install(self):
        try:
            zip = ZipFile(self.filename)
            zip.extractall('/Applications/World of Warcraft/Interface/AddOns/')
        finally:
            zip.close()


def is_nested():
    try:
        zip = ZipFile('TradeSkillMaster-v3.4.16.zip')
        files = zip.namelist()
        tocs = [f for f in files if f.endswith('.toc')]
    finally:
        zip.close()


@retry(stop_max_attempt_number=3)
def install(addon):
    click.echo('Installing addon ' + addon)
    addon = AddOn(addon)
    addon.load()
    addon.fetch()
    addon.install()


@click.group(help='A command to install AddOns from Curse')
@click.option('--debug/--no-debug', default=False, help='Outputs debugging info.')
@click.pass_context
def cli(ctx, debug):
    ctx.obj['DEBUG'] = debug


@cli.command('list', help='List Installed AddOns')
@click.pass_context
def list_addons(ctx):
    for a in sorted(known_addons):
        click.echo(a)


@cli.command('install', help='Install AddOns')
@click.argument('addons', nargs=-1)
@click.pass_context
def install_addons(ctx, addons):
    for a in sorted(addons):
        install(a)
        known_addons.add(a)

    with open('addons.txt', 'w') as f:
        lines = '\n'.join(sorted(known_addons))
        f.write(lines)


@cli.command('update', help='Update AddOns')
@click.argument('addons', nargs=-1)
@click.pass_context
def update_addons(ctx, addons):
    if not addons:
        addons = known_addons

    for a in addons:
        install(a)


def main():
    return cli(obj={})

if __name__ == '__main__':
    cli(obj={})
