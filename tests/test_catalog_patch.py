import copy
import unittest

from scripts.install import InstallError, ULTRA_DESCRIPTION, add_luna_ultra


def make_catalog():
    return {
        "models": [
            {
                "slug": "gpt-6-luna",
                "multi_agent_version": "v2",
                "supported_reasoning_levels": [
                    {"effort": "low", "description": "low"},
                    {"effort": "max", "description": "max"},
                ],
            },
            {"slug": "other-model", "custom_metadata": {"keep": True}},
        ]
    }


class CatalogPatchTests(unittest.TestCase):
    def test_adds_ultra_after_max_and_preserves_other_models(self):
        catalog = make_catalog()
        other_before = copy.deepcopy(catalog["models"][1])

        result = add_luna_ultra(catalog)

        luna = result["models"][0]
        efforts = [level["effort"] for level in luna["supported_reasoning_levels"]]
        self.assertEqual(efforts, ["low", "max", "ultra"])
        self.assertEqual(luna["supported_reasoning_levels"][-1]["description"], ULTRA_DESCRIPTION)
        self.assertEqual(luna["multi_agent_reasoning_effort"], "max")
        self.assertEqual(result["models"][1], other_before)

    def test_patch_is_idempotent(self):
        once = add_luna_ultra(make_catalog())
        twice = add_luna_ultra(copy.deepcopy(once))
        self.assertEqual(twice, once)

    def test_preserves_provider_native_ultra_description_and_effort(self):
        catalog = make_catalog()
        luna = catalog["models"][0]
        luna["supported_reasoning_levels"].append(
            {"effort": "ultra", "description": "Provider native ultra", "provider_field": "keep"}
        )
        luna["multi_agent_reasoning_effort"] = "xhigh"

        result = add_luna_ultra(catalog)
        levels = result["models"][0]["supported_reasoning_levels"]
        self.assertEqual([level["effort"] for level in levels], ["low", "max", "ultra"])
        self.assertEqual(levels[-1]["description"], "Provider native ultra")
        self.assertEqual(levels[-1]["provider_field"], "keep")
        self.assertEqual(result["models"][0]["multi_agent_reasoning_effort"], "xhigh")

    def test_rejects_unhashable_or_invalid_slugs(self):
        for bad_slug in ([], None, ""):
            with self.subTest(slug=bad_slug):
                catalog = make_catalog()
                catalog["models"][1]["slug"] = bad_slug
                with self.assertRaises(InstallError):
                    add_luna_ultra(catalog)

    def test_rejects_malformed_or_duplicate_efforts(self):
        for levels in (
            [{"effort": "max"}, None],
            [{"effort": "max"}, {"effort": []}],
            [{"effort": "max"}, {"effort": "max"}],
        ):
            with self.subTest(levels=levels):
                catalog = make_catalog()
                catalog["models"][0]["supported_reasoning_levels"] = levels
                with self.assertRaises(InstallError):
                    add_luna_ultra(catalog)

    def test_rejects_duplicate_slugs(self):
        catalog = make_catalog()
        catalog["models"][1]["slug"] = "gpt-6-luna"
        with self.assertRaises(InstallError):
            add_luna_ultra(catalog)


if __name__ == "__main__":
    unittest.main()
