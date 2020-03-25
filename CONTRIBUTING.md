
# Contributing to Maestro

Thanks for checking out Maestro! We've put together the following guidelines to help you figure out where you can best be helpful. Interested in making a contribution? Read on!

## Submit a commandline idea for faster remote work

Do you have an idea for a maestro commandline tool for fast remote work? You can submit a feature request [here](https://gitlab.science.gc.ca/CMOI/maestro/issues). However please provide example "input" and "output" so we know precisely what you are looking for. For example:

This is the command I want to run:

```
m.flow /home/smco500/.suites/gdps/verification --filter=abort,waiting --date=2020032200
```

and this is the output I want to see:

```
gdps_verif/SCORES_VS_OBSERVATIONS/Geps_mean_scores ABORT
gdps_verif/SCORES_VS_OBSERVATIONS/residus_alt WAITING
```

where "ABORT" is red.

## Submit a bug report

Found a bug? You can submit a new bug report [here](https://gitlab.science.gc.ca/CMOI/maestro/issues). Select the "bug" template.

## Submit a feature request

Have an idea for a new feature? You can submit a feature request [here](https://gitlab.science.gc.ca/CMOI/maestro/issues). Select the "feature" template.

## Guidelines

1. If you open a  [merge requests](https://gitlab.science.gc.ca/CMOI/maestro/merge_requests), please ensure that your contribution passes all tests. If there are test failures, you will need to address them before we can merge your contribution.
1. When adding content, please consider if it is widely valuable. A simple feature written for just one person still adds complexity to the project.
1. Always seek code review from at least one other developer before merging your changes. [Here's a short video](https://www.youtube.com/watch?v=0AT7JxqoIps&list=PLRf-PfhVvwFA7tGxwEgxgnJIY7aVevqqo) about how you might share your work for a code review and merge.

## How to contribute code

This section is for developers who are thinking of making any contribution to the repository, big or small.

Develop all your changes on a new branch, not on `master`. The only commits on the `master` branch should be tagged versions that also a published SSM available to all.

If you'd like to contribute, start by searching through the [issues](https://gitlab.science.gc.ca/CMOI/maestro/issues) and [merge requests](https://gitlab.science.gc.ca/CMOI/maestro/merge_requests) to see whether someone else has raised a similar idea or question.

If you don't see your idea listed, and you think it fits into the goals of this guide, do one of the following:

* **If your contribution is minor,** such as a typo fix, open a [merge request](https://www.youtube.com/watch?v=0AT7JxqoIps&list=PLRf-PfhVvwFA7tGxwEgxgnJIY7aVevqqo).
* **If your contribution is major,** such as a new feature or many commits, start by opening an issue first. That way, other people can weigh in on the discussion before you do any work.

## Man Pages

Some of the maestro tools have Linux man pages:

```
man xflow
```

If you make changes to commandline tools, or add new commandline tools, consider updating or creating the man page. You do this by writing markdown files, found in the `maestro/man/markdown` folder.

## New Releases

This section is for developers who are thinking of releasing an official version of maestro.

These are the steps you should follow:

1. Develop all your changes on a new branch, for example `release-1.6`.
1. Run the test suite. All tests must pass.
1. Verify that all [issues](https://gitlab.science.gc.ca/CMOI/maestro/issues) for this milestone and version are resolved.
1. Manually test all [user stories](USER_STORIES.md).
1. Tag your commit. Example: `git tag -a 1.6.3`. You may also want to do `git push --tags`.
1. Create, install, and publish the SSM package in a location similar to previous versions.
1. Merge the release branch, for example `release-1.6` onto the `master` branch. Only tagged, published versions should be on the `master` branch.
1. Upgrade the live operational versions of Maestro by following [these instructions](https://wiki.cmc.ec.gc.ca/wiki/Maestro/Update).
1. Write release notes for this version on the wiki. [Here's an example](https://wiki.cmc.ec.gc.ca/wiki/Maestro/1.6.0).
1. Send an email to the Maestro mailing list.
1. Post a message in the Maestro chat.

## Community

Discussions about Maestro take place on this repository's [issues](https://gitlab.science.gc.ca/CMOI/maestro/issues) and [merge requests](https://gitlab.science.gc.ca/CMOI/maestro/merge_requests) sections. Anybody is welcome to join these conversations. 

Wherever possible, do not take these conversations to private channels, including contacting the maintainers directly. Keeping communication public means everybody can benefit and learn from the conversation.

## See Also

* [GCcollab chat about Maestro](https://message.gccollab.ca/channel/maestro).
* [Maestro mailing list](http://internallists.cmc.ec.gc.ca/cgi-bin/mailman/listinfo/maestro_users).
* [Maestro wiki page on the CMC wiki](https://wiki.cmc.ec.gc.ca/wiki/Maestro) with training resources, documentation, and release notes.
* There are some introduction to Maestro tutorial videos on the [Computer Specialist (CS) Training for Public Servants](https://www.youtube.com/playlist?list=PLRf-PfhVvwFA7tGxwEgxgnJIY7aVevqqo) playlist.
