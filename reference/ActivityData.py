#import
from git import Repo
        join = osp.join

# rorepo is a Repo instance pointing to the git-python repository.
repo = Repo(self.rorepo.working_tree_dir)
assert not repo.bare


tree = repo.heads.master.commit.tree
        assert len(tree.hexsha) == 40
        
assert len(tree.trees) > 0          # trees are subdirectories
        assert len(tree.blobs) > 0          # blobs are files
        assert len(tree.blobs) + len(tree.trees) == len(tree)
