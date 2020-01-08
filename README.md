### TODO

- Finish writing tests
- Setup CircleCI on GitHub
- Write a Procfile for deployment

### Future

- Use `alembic` for migrations
- Write some alternative storage classes--probably S3 to start

### Assignment

- Return a random set of N-second clips from the entire audio corpus
- Add a /download?uuid={uuid}&start=N&stop=N route (maybe)
- Can potentially do the random generation on the client side rather than on the backend
- Need something to decode MP3s, probably a library to handle WAV files (though IIRC the format
  is pretty simple already)
- Probably just return a tarball of all the clips instead of implementing a paginator with single
  downloads
- Would be nice if a random set of clips could be downloaded /again/ with some UUID or something
  instead of disappearing after being generated