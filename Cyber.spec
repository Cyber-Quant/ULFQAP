# -*- mode: python ; coding: utf-8 -*-

block_cipher = pyi_crypto.PyiBlockCipher(key='xxxxxxxxxxxxxxxx')


a = Analysis(['main.py'],
             pathex=['/Users/jia/Desktop/cyberpunk'],
             binaries=[],
             datas=[
             ('media/backtest.svg', 'media'),
             ('media/choose.svg', 'media'),
             ('media/down.wav', 'media'),
             ('media/license.html', 'media'),
             ('media/logo.svg', 'media'),
             ('media/logo.ico', 'media'),
             ('media/logo.icns', 'media'),
             ('media/long.png', 'media'),
             ('media/setting.svg', 'media'),
             ('media/short.png', 'media'),
             ('media/splash.jpg', 'media'),
             ('media/up.wav', 'media'),
             ('media/watch.svg', 'media'),
             ('user_data/apply_strategies.json', 'user_data'),
             ('user_data/conf.json', 'user_data'),
             ('user_data/custom_watch.json', 'user_data'),
             ('user_data/fav_stocks.json', 'user_data'),
             ('user_data/quant.db', 'user_data'),
             ('user_data/rules/boll.json', 'user_data/rules')
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Cyber',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='media/logo.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Cyber')
app = BUNDLE(coll,
             name='Cyber.app',
             icon='media/logo.icns',
             bundle_identifier=None)
