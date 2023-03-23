# Pathfinder-Wrath-of-the-Righteous-Build-Tool
The Pathfinder: Wrath of the Righteous Build Tool is used to store and recall your builds for the The Pathfinder: Wrath of the Righteous video game.

This is my first public release.
There is a digitial signature signed by http://timestamp.digicert.com located in the "data"folder. This file should be installed into your "Trusted Certificates" if your system detects the file as malware.
The software reads and writes to a database file called "pathfinder.db" which is located in the "data"folder.
if this file is not available, the program will not run.


**The Pathfinder: Wrath of the Righteous Build Tool**

Quick Guide




__**View a Build**__

-This tab allows you to view the Builds that have been entered into the application database.
- I have included the Builds that I use.
1. Select the Character Name from the drop-down.
	- This does include all Companions including new Shifter companion
2. Select the "Build Type".
	- this is the name of the build.
3. Select the "Character Level".
	- only the created levels will appear
		- For example, if you have only created a build for up to level 5, you will only have 5 levels to select.
			if you have created 20 levels, then you will see 20.
	- Please note that for Legend Mytyhic Path, you are able to go above 20 levels.
	- The DEFAULT builds provided will be up to 20 levels.
4. Click the "Load" button.
5. The application will load the data from the database for your build at the specified or choosen level.







__**View Mythic Feat**__
1. Select the Character Name from the drop-down.
2. Select the "Build Type".
	- this is the name of the build.
3. Select the Character's Mythic level in the "Character Level" drop-down.
	- only the created levels will appear 
4. Click the "Load" button.
5. The application will load the data from the database for the Character at the specified or choosen Mythic level.







__**Create a Build**__
-This tab allows you to Create Builds that have been entered into the application database.
- I have included the Builds that I use.
1. Select the Character Name from the drop-down.
	- This does include all Companions including new Shifter companion
2. Enter the "Build Type".
	- this is the name of the build for the character.
	- at this time it is not a drop-down with current builds. my apologies as i am working on this feature.
3. Select the "Character Level".
	- you may enter the level number with keyboard or select the level from the drop-down
		- Please note that for Legend Mytyhic Path, you are able to go above 20 levels. For every level over 20, you will need to enter in the level at this time.
	- The DEFAULT builds provided will be up to 20 levels.
4. Enter the Class name for the level.
	- Many players multi-class so i have added this for those options.
	- For example:
		Alchemist>Vivisectionist
5. Enter in the values as needed for the selected level.
6. Click "Create Build" to create the build and save the level.
7. Repeat steps 1-5 for all levels for the build.

__**NOTE:**__
Feats, Class Feats and Spells are drop-down fields that are populated from the database but you may also type in text as well.

Please note that these drop-downs were populated with the latest values on 3-20-2023. So they should be up to date.

- You may enter values manually but the values entered will not be stored in the lists for Feats, Class Feats or Spells.
	They WILL be stored in your build database!









__**Add/Update Mythic Feat**__
-This tab allows you to add Mythic Feats to your character build for use when Leveling up your Mythic Feats.
- I have included the Builds that I use.
1. Select the Character Name from the drop-down.
	- This does include all Companions including new Shifter companion
	- This will include ANY new builds you have created.
2. Enter or select an existing "Build Type" for the Character.
	- this is the name of the build for the character.
3. Select the Mythic Level the feat is for with the drop-down for "Character Level".
	- you may enter the level number with keyboard or select the level from the drop-down
		- Please note that for Legend Mytyhic Path, you are able to go above 20 levels. For every level over 10, you will need to enter in the level at this time.
	- The DEFAULT builds provided will be up to 10 levels.
4. Select the Mythic Feat with the drop-down for "Mythic Path"
	- This list is auto-populated with Mythic Feats that were present in game as of 3-20-2023
5. Click the "Add Mythic Feat" to create the build and save.
7. Repeat steps 1-5 for all levels for all levels.







__**Delete A Build**__
- This tab allows you to delete a Build from the application.
1. Select the Character Name from the drop-down.
2. Select the "Build Type" for the Character.
3. Select the "Character Level".
4. Click "Delete Build".
5. Confirm Delete in the pop-up.

__**NOTE: **__
Clear button is used to clear the all fields of information.

You may:
a. Delete the entire Character from the database
b. Delete a single Build from the Character.
c. Delete just one level from the build for the Character.








__**Delete Mythic Feat**__
- This tab allows you to delete a Mythic Feat from the application.
1. Select the Character Name from the drop-down.
2. Select the "Build Type" for the Character.
3. Select the "Character Level".
4. Select the "Mythic Feat" to delete
5. Click "Delete Build".
6. Confirm Delete in the pop-up.
