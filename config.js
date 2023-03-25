/*
  Copyright (C) 2016 Apple Inc. All Rights Reserved.
  See LICENSE.txt for this sample’s licensing information
  
  Abstract:
  This is the container configuration that gets passed to CloudKit.configure.
        Customize this for your own environment.
 */

module.exports = {
  // // The API key to use for Apple iCloud
  containerIdentifier:'iCloud.com.duskmount.lightfrozen.languagebuddy',
  zoneID: "_defaultZone",
  environment: 'development',
  serverToServerKeyAuth: {
    // Generate a key ID through CloudKit Dashboard and insert it here.
    keyID: '5e47fc724d2f042a10bfcf69144b147a4194c05fc78e5fa122733e6faeca45b3',

    // This should reference the private key file that you used to generate the above key ID.
    privateKeyFile: __dirname + '/eckey2.pem'
  },

  // The API key to use for Openai GTP-3
  organization: "org-N7pwJUdlx1SYcAUFyAnFqwqr",
  apiKey: "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",


  // The API key to use for Mircrosoft azure text to speech
  azure_speech_key: "131074b007474b378244fe956f535288",
  azure_speech_region: "eastus",

};

